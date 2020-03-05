#!/usr/bin/env bash
##
# Build site in CI.
#
set -e

# Process Docker Compose configuration. This is used to avoid multiple
# docker-compose.yml files.
# Remove lines containing '###'.
sed -i -e "/###/d" docker-compose.yml
# Uncomment lines containing '##'.
sed -i -e "s/##//" docker-compose.yml

# Pull the latest images.
ahoy pull

# Disable checks used on host machine.
export DOCTOR_CHECK_PYGMY=0
export DOCTOR_CHECK_PORT=0
export DOCTOR_CHECK_SSH=0
export DOCTOR_CHECK_WEBSERVER=0
export DOCTOR_CHECK_BOOTSTRAP=0

ahoy build
