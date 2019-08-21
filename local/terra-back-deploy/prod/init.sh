#! /bin/bash
# AS root
set -ex
SCRIPTSDIR="$(dirname $(readlink -f "$0"))"
cd "$SCRIPTSDIR/.."
TOPDIR=$(pwd)
export APP_TYPE="${APP_TYPE:-docker}"
export APP_USER="${APP_USER:-$APP_TYPE}"
export APP_GROUP="$APP_USER"
export USER_DIRS=". public/media"
for i in $USER_DIRS;do
    if [ ! -e "$i" ];then mkdir -p "$i";fi
    chown $APP_USER:$APP_GROUP "$i"
done
if (find /etc/sudoers* -type f 2>/dev/null);then chown -Rf root:root /etc/sudoers*;fi
exec gosu $APP_USER:$APP_GROUP bash -c "init/start.sh $@"
