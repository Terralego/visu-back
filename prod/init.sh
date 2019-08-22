#! /bin/bash
# AS root
set -ex
chown django:django ../public/media/
exec gosu django:django bash -c "../init/start.sh"
