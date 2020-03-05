#!/usr/bin/env sh
set -e

dockerize -wait tcp://postgres:5432 -timeout 1m
dockerize -wait tcp://solr:8983 -timeout 1m

sed -i "s@SITE_URL@${SITE_URL}@g" /app/ckan/default/production.ini

. /app/ckan/default/bin/activate \
    && paster serve /app/ckan/default/production.ini
