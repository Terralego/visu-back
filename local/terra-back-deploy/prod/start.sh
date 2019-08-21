#! /bin/bash
# AS $user
set -e
SCRIPTSDIR="$(dirname $(readlink -f "$0"))"
cd "$SCRIPTSDIR/.."
TOPDIR=$(pwd)
cd src
# load locales & default env
for i in /etc/environment /etc/default/locale;do if [ -e $i ];then . $i;fi;done
. ../venv/bin/activate
# Regenerate egg-info & be sure to have it in site-packages
regen_egg_info() {
    local f="$1"
    if [ -e "$f" ];then
        local e="$(dirname "$f")"
        echo "Reinstalling egg-info in: $e" >&2
        ( cd "$e" && python setup.py egg_info ; )
    fi
}
set -x
GUNICORN_CLASS=${GUNICORN_CLASS:-sync}
GUNICORN_EXTRA_ARGS="${GUNICORN_EXTRA_ARGS-}"
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
DJANGO_LISTEN=${DJANGO_LISTEN:-"0.0.0.0:8000"}
NO_MIGRATE=${NO_MIGRATE-}
NO_COLLECT_STATIC=${NO_COLLECT_STATIC-}
NO_GUNICORN=${NO_GUNICORN-}
NO_START=${NO_START-}
DJANGO_WSGI=${DJANGO_WSGI:-project.wsgi}
# regenerate any setup.py found as it can be an egg mounted from a docker volume
# without having a change to be built
while read f;do regen_egg_info "$f";done < <( \
  find "$TOPDIR/setup.py" "$TOPDIR/src" "$TOPDIR/lib" \
    -name setup.py -type f -maxdepth 2 -mindepth 0; )

# Run any migration
if [[ -z ${NO_MIGRATE} ]];then
    ./manage.py migrate --noinput
fi
# Collect statics
if [[ -z ${NO_COLLECT_STATIC} ]];then
    ./manage.py collectstatic --noinput
fi
# Run app
if [[ -z ${NO_START} ]];then
    if [[ -z ${NO_GUNICORN} ]];then
        exec gunicorn $DJANGO_WSGI -w $GUNICORN_WORKERS -b $DJANGO_LISTEN -k $GUNICORN_CLASS $GUNICORN_EXTRA_ARGS
    else
        exec ./manage.py runserver $DJANGO_LISTEN
    fi
else
    while true;do echo "start skipped" >&2;sleep 65535;done
fi
