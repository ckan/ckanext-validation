#!/usr/bin/env sh
set -e

. `dirname $0`/activate
ckan -c ${CKAN_INI} run --disable-reloader --threaded
