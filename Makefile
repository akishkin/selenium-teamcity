PACKAGE_NAME=selenium-teamcity
VERSION=1.0

clean:
    rm -rf build/ MANIFEST
    find . -name '*.py[co]' -delete

test_prepare:
    service postgresql start version 9.3
    createdb -p 5433 selenium_teamcity
    npm install
    node_modules/.bin/gulp

ci_selenium: clean test_prepare resetdb_ci
    POSTGRESQL_PORT=5433
    xvfb-run --server-args="-screen 0, 1024x768x24" py.test selenium_tests --browsers='Firefox, Chrome' --ds=selenium_tests.settings --teamcity

selenium_test:
    py.test selenium_tests --local-test

resetdb_ci:
    POSTGRESQL_PORT=5433 ./manage.py reset_db --noinput --settings=selenium_tests.settings
    POSTGRESQL_PORT=5433 ./manage.py migrate --noinput --settings=selenium_tests.settings
    POSTGRESQL_PORT=5433 ./manage.py create_admin --settings=selenium_tests.settings
    POSTGRESQL_PORT=5433 ./manage.py reset_permissions --settings=selenium_tests.settings
    POSTGRESQL_PORT=5433 ./manage.py create_languages --settings=selenium_tests.settings
    POSTGRESQL_PORT=5433 ./manage.py create_picklists --settings=selenium_tests.settings

.PHONY: all clean test_prepare resetdb_ci selenium_test ci_selenium
