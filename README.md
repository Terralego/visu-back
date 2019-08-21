# Initialise your development environment

All following commands must be run only once at project installation.

## First clone

```sh
git clone <>
```

## Install docker and docker compose

if you are under debian/ubuntu/mint/centos you can do the following:

Follow official procedures for
  [docker](https://docs.docker.com/install/#releases) and
  [docker-compose](https://docs.docker.com/compose/install/).



## Configuration

Copy configuration files from their ``.dist`` counterpart
and adapt them to your needs.

cp Docker.env.dist Docker.env

cp .env.dist .env

cp src/project/settings/local.py.dist local.py

**Hint**: You may have to add `0.0.0.0` to `ALLOWED_HOSTS` in `local.py`.

# Use your development environment

## Start the stack

After a last verification of the files, to run with docker, just type:

```bash
# First time you download the app, or sometime to refresh the image
docker-compose -f docker-compose.yml -f docker-compose-dev.yml pull # Call the docker compose pull command
docker-compose -f docker-compose.yml -f docker-compose-build-dev.yml build # Should be launched once each time you want to start the stack
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up # Should be launched once each time you want to start the stack
```

## Test
curl http://localhost:<port>/api/settings/

## Start a shell inside the django container

- for user shell

    ```sh
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django bash
    ```
- for root shell

    ```sh
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django bash
    ```


## Rebuild/Refresh local docker image in dev

```sh
    docker-compose -f docker-compose.yml -f docker-compose-dev.yml -f docker-compose-build-dev.yml build
```

## Calling Django manage commands

```sh
docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django /local/venv/bin/python /local/code/manage.py shell [options]
# For instance:
# docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django /local/venv/bin/python /local/code/manage.py shell migrate
# docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django /local/venv/bin/python /local/code/manage.py shell shell
# docker-compose -f docker-compose.yml -f docker-compose-dev.yml exec django /local/venv/bin/python /local/code/manage.py shell createsuperuser
# ...
```

## Run tests

```sh
# also consider: linting|coverage
```

## Docker volumes

Your application extensively use docker volumes. From times to times you may
need to erase them (eg: burn the db to start from fresh)

```sh
docker volume ls  # hint: |grep \$app
docker volume rm $id
```

## FAQ

If you get troubles with the nginx docker env restarting all the time, try recreating it :

```bash
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d --no-deps --force-recreate nginx backup
```

If you get the same problem with the django docker env :

```bash
docker-compose -f docker-compose.yml -f docker-compose-dev.yml stop django db
docker volume rm visu-postgresql # check with docker volume ls
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d db
# wait fot postgis to be installed
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up django
```

## Troobleshouting
elasticsearch_1   | [1]: max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
  sudo sysctl -w vm.max_map_count=262144

  sudo vim /etc/sysctl.conf -> vm.max_map_count=262144