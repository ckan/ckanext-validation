#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Postgres version"
psql --version

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install solr-jetty

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKAN_VERSION != 'master' ]
then
    git checkout $CKAN_VERSION
fi
# Unpin CKAN's psycopg2 dependency get an important bugfix
# https://stackoverflow.com/questions/47044854/error-installing-psycopg2-2-6-2
sed -i '/psycopg2/c\psycopg2' requirements.txt
python setup.py develop
pip install -r requirements.txt
pip install -r dev-requirements.txt
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

echo "Installing other extensions requirements..."
git clone https://github.com/ckan/ckanext-scheming
cd ckanext-scheming
pip install -r requirements.txt
python setup.py develop
cd -
if [ $CKAN_VERSION == 'dev-v2.6' ] || [ $CKAN_VERSION == 'release-v2.5-latest' ] || [ $CKAN_VERSION == 'release-v2.4-latest' ]
then
	git clone https://github.com/ckan/ckanext-rq
	cd ckanext-rq
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	python setup.py develop
	cd -
	# Enable the rq plugin
	sed -i -e 's/ckan.plugins = /ckan.plugins = rq /' test.ini
fi

echo "Installing ckanext-validation and its requirements..."
python setup.py develop
pip install -r requirements.txt
pip install -r dev-requirements.txt
paster --plugin=ckanext-validation validation init-db -c ckan/test-core.ini

echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

echo "travis-build.bash is done."
