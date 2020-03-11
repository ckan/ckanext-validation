#!/usr/bin/env sh
##
# Initialise CKAN instance.
#
set -e

CKAN_INI_FILE=/app/ckan/default/production.ini
CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_USER_PASSWORD="${CKAN_USER_PASSWORD:-Password123!}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"

. /app/ckan/default/bin/activate \
  && cd /app/ckan/default/src/ckan \
  && paster db clean -c $CKAN_INI_FILE \
  && paster db init -c $CKAN_INI_FILE \
  && paster --plugin=ckanext-validation validation init-db -c $CKAN_INI_FILE \
  && paster --plugin=ckan user add "${CKAN_USER_NAME}" email="${CKAN_USER_EMAIL}" password="${CKAN_USER_PASSWORD}" -c $CKAN_INI_FILE \
  && paster --plugin=ckan sysadmin add "${CKAN_USER_NAME}" -c $CKAN_INI_FILE

# Create some base test data
. /app/scripts/create-test-data.sh
