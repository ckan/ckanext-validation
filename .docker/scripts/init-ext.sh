#!/usr/bin/env sh
##
# Install current extension.
#
set -e

. /app/ckan/default/bin/activate

pip install -r "/app/requirements.txt"
pip install -r "/app/dev-requirements.txt"
python setup.py develop
installed_name=$(grep '^\s*name=' setup.py |sed "s|[^']*'\([-a-zA-Z0-9]*\)'.*|\1|")

# Validate that the extension was installed correctly.
if ! pip list | grep "$installed_name" > /dev/null; then echo "Unable to find the extension in the list"; exit 1; fi

deactivate
