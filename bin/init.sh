#!/usr/bin/env sh
##
# Initialise CKAN data for testing.
#
set -e

. "${APP_DIR}"/bin/activate
CLICK_ARGS="--yes" ckan_cli db clean
ckan_cli db init
# apply any plugin migrations
ckan_cli db upgrade

# Initialise validation tables
ckan_cli validation init-db
