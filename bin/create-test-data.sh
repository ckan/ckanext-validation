#!/usr/bin/env sh
##
# Create some example content for extension BDD tests.
#
set -ex

# Set APP_DIR if not already set

# Set path to source bin if not found on path
if ! type ckan_cli &> /dev/null; then
  APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  export PATH=${APP_DIR}/bin:$PATH
fi

CKAN_ACTION_URL=${CKAN_SITE_URL}api/action
CKAN_USER_NAME="${CKAN_USER_NAME:-admin}"
CKAN_DISPLAY_NAME="${CKAN_DISPLAY_NAME:-Administrator}"
CKAN_USER_EMAIL="${CKAN_USER_EMAIL:-admin@localhost}"

. "${APP_DIR}"/bin/activate

add_user_if_needed () {
    echo "Adding user '$2' ($1) with email address [$3]"
    ckan_cli user show "$1" | grep "$1" || ckan_cli user add "$1"\
        fullname="$2"\
        email="$3"\
        password="${4:-Password123!}"
}

api_call () {
    wget -O - --header="Authorization: ${API_KEY}" --post-data "$1" ${CKAN_ACTION_URL}/$2
}

add_user_if_needed "$CKAN_USER_NAME" "$CKAN_DISPLAY_NAME" "$CKAN_USER_EMAIL"
ckan_cli sysadmin add "${CKAN_USER_NAME}"

API_KEY=$(ckan_cli user show "${CKAN_USER_NAME}" | tr -d '\n' | sed -r 's/^(.*)apikey=(\S*)(.*)/\2/')
if [ "$API_KEY" = "None" ]; then
    echo "No API Key found on ${CKAN_USER_NAME}, generating API Token..."
    API_KEY=$(ckan_cli user token add "${CKAN_USER_NAME}" test_setup |tail -1 | tr -d '[:space:]')
fi

##
# BEGIN: Create a test organisation with test users for admin, editor and member
#
TEST_ORG_NAME=test-organisation
TEST_ORG_TITLE="Test Organisation"

echo "Creating test users for ${TEST_ORG_TITLE} Organisation:"

add_user_if_needed ckan_user "CKAN User" ckan_user@localhost
add_user_if_needed test_org_admin "Test Admin" test_org_admin@localhost
add_user_if_needed test_org_editor "Test Editor" test_org_editor@localhost
add_user_if_needed test_org_member "Test Member" test_org_member@localhost

echo "Creating ${TEST_ORG_TITLE} organisation:"

TEST_ORG=$( \
    api_call '{"name": "'"${TEST_ORG_NAME}"'", "title": "'"${TEST_ORG_TITLE}"'",
        "description": "Organisation for testing issues"}' organization_create
)
#echo $TEST_ORG
TEST_ORG_ID=$(echo $TEST_ORG | ${PYTHON-python3} "${APP_DIR}"/bin/extract-id.py)

echo "Assigning test users to '${TEST_ORG_TITLE}' organisation (${TEST_ORG_ID}):"

api_call '{"id": "'"${TEST_ORG_ID}"'", "object": "test_org_admin", "object_type": "user", "capacity": "admin"}' member_create

api_call '{"id": "'"${TEST_ORG_ID}"'", "object": "test_org_editor", "object_type": "user", "capacity": "editor"}' member_create

api_call '{"id": "'"${TEST_ORG_ID}"'", "object": "test_org_member", "object_type": "user", "capacity": "member"}' member_create

##
# END.
#

. "${APP_DIR}"/bin/deactivate
