#!/bin/bash
set -e

echo "This is travis-build.bash..."

# Drop Travis' postgres cluster if we're building using a different pg version
TRAVIS_PGVERSION='9.1'
if [ $PGVERSION != $TRAVIS_PGVERSION ]
then
  # Make psql use $PGVERSION
  export PGCLUSTER=$PGVERSION/main
fi
echo "Postgres version"
psql --version

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install postgresql-$PGVERSION solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION != 'master' ]
then
    git checkout release-v$CKANVERSION-latest
fi
python setup.py develop
pip install -r requirements.txt --allow-all-external
pip install -r dev-requirements.txt --allow-all-external
cd -

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "SOLR config..."
# Solr is multicore for tests on ckan master, but it's easier to run tests on
# Travis single-core. See https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini

echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
cd -

echo "Installing ckanext-validation and its requirements..."
python setup.py develop
pip install -r requirements.txt
paster --plugin=ckanext-validation validation init-db -c ckan/test-core.ini

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
