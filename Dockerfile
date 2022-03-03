ARG BASE=corpusops/ubuntu-bare:focal
FROM $BASE
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ARG BUILD_DEV=y
ARG PY_VER=3.8
# See https://github.com/nodejs/docker-node/issues/380
ARG GPG_KEYS=B42F6819007F00F88E364FD4036A9C25BF357DD4
ARG GPG_KEYS_SERVERS="hkp://p80.pool.sks-keyservers.net:80 hkp://ipv4.pool.sks-keyservers.net hkp://pgp.mit.edu:80"

WORKDIR /code
ADD apt.txt /code/apt.txt

RUN bash -c 'set -ex \
  && : "install packages" \
  && apt-get update -qq \
  && apt-get -y -qq upgrade \
  && apt-get install -y -qq netcat tzdata \
  && apt-get install -qq -y $(grep -vE "^\s*#" /code/apt.txt  | tr "\n" " ") \
  && apt-get clean all && apt-get autoclean \
  && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/* \
  && : "project user & workdir" \
  && mkdir -p /share/tmp \
  && useradd -ms /bin/bash django --uid 1000'

ADD prod/start.sh \
  prod/cron.sh \
  prod/init.sh \
  /code/init/

ADD requirements*.txt tox.ini README.md /code/
ADD src /code/src/
ADD private /code/private/
ADD lib /code/lib

RUN bash -c 'set -ex \
  && chown django:django -R /code \
  && chown django:django /share/tmp \
  && cd /code \
  && gosu django:django bash -c "python3.8 -m venv venv \
  && venv/bin/pip install -U --no-cache-dir setuptools wheel pip \
  && if [[ -n "$BUILD_DEV" ]];then \
  venv/bin/pip install -U --no-cache-dir -r ./requirements-dev.txt;\
  else \
  venv/bin/pip install -U --no-cache-dir -r ./requirements.txt; \
  fi \
  && mkdir -p public/static public/media"'

# image will drop privileges itself using gosu
WORKDIR /code/src
CMD "/code/init/init.sh"
