import functools
import pytest

from django.db import connections
from django.test.runner import DiscoverRunner


runner = DiscoverRunner(verbosity=pytest.config.option.verbose, interactive=False)


def _sql_table_creation_suffix(self):
    return 'WITH TEMPLATE %s' % self.connection.settings_dict['ORIGINAL_NAME']


def _create_test_db(self, verbosity=1, autoclobber=False, serialize=True):
    test_database_name = self._get_test_db_name()

    if verbosity >= 1:
        test_db_repr = ''
        if verbosity >= 2:
            test_db_repr = " ('%s')" % test_database_name
        print "Creating test database for alias '%s'%s..." % (
            self.connection.alias, test_db_repr)

    self.connection.settings_dict['ORIGINAL_NAME'] = self.connection.settings_dict['NAME']
    self._create_test_db(verbosity, autoclobber)

    self.connection.close()
    self.connection.settings_dict['NAME'] = test_database_name
    self.connection.cursor()

    return test_database_name


def patch_connections():
    for connection in connections.all():
        connection.creation.sql_table_creation_suffix = functools.partial(
            _sql_table_creation_suffix, connection.creation)
        connection.creation.create_test_db = functools.partial(
            _create_test_db, connection.creation)


def setup_databases(cursor_wrapper):
    with cursor_wrapper:
        return runner.setup_databases()


def teardown_databases(cursor_wrapper, config):
    with cursor_wrapper:
        return runner.teardown_databases(config)


def reload_databases(cursor_wrapper):
    with cursor_wrapper:
        for connection in connections.all():
            connection.creation.destroy_test_db(
                connection.settings_dict['ORIGINAL_NAME'], 0)
            connection.settings_dict['NAME'] = connection.settings_dict['ORIGINAL_NAME']
            connection.creation.create_test_db(verbosity=0)

