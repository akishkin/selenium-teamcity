import os
import re
import pytest
from selenium_wrapper import SeleniumWrapper


SCREENSHOTS_DIR = 'screenshots'
DEFAULT_BROWSERS = ['Firefox']


def pytest_addoption(parser):
    parser.addoption('--local-test', action='store_true')
    parser.addoption('--browsers', default='')


def pytest_generate_tests(metafunc):
    if 'browser' in metafunc.fixturenames:
        browsers = filter(lambda x: x, metafunc.config.option.browsers.split(','))
        metafunc.parametrize('browser', browsers or DEFAULT_BROWSERS)


def _get_teamcity_plugin(plugins):
    try:
        from teamcity.pytest_plugin import EchoTeamCityMessages
    except ImportError:
        return None
        
    for plugin in plugins:
        if isinstance(plugin, EchoTeamCityMessages):
            return plugin
    return None


def _make_screenshot_path(nodeid):
    testid = re.sub(r'[_/:\(\)\[\]\s,|]+', '_', nodeid)
    return os.path.join(SCREENSHOTS_DIR, '{}.png'.format(testid))


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    report = __multicall__.execute()

    if report.when != 'call' or not report.failed or 'selenium_driver' not in item.funcargs:
        return report

    teamcity = _get_teamcity_plugin(item.getplugins())
    if not teamcity:
        return report

    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    selenium_driver = item.funcargs['selenium_driver']
    screenshots_path = _make_screenshot_path(item.nodeid)
    selenium_driver.get_driver().get_screenshot_as_file(screenshots_path)
    teamcity.teamcity.publishArtifacts(screenshots_path)
    return report

@pytest.fixture(scope='session')
def local_test(request):
    return request.config.option.local_test


@pytest.fixture(scope='session')
def _django_db_setup(request, _django_test_environment, _django_cursor_wrapper):
    from .utils import patch_connections, setup_databases, teardown_databases

    patch_connections()
    config = setup_databases(_django_cursor_wrapper)
    request.addfinalizer(lambda: teardown_databases(_django_cursor_wrapper, config))


@pytest.fixture(scope='function', autouse=True)
def transactional_db(request, local_test):
    if local_test:
        return

    from .utils import reload_databases

    request.getfuncargvalue('_django_db_setup')
    _django_cursor_wrapper = request.getfuncargvalue('_django_cursor_wrapper')

    _django_cursor_wrapper.enable()
    request.addfinalizer(_django_cursor_wrapper.disable)
    request.addfinalizer(lambda: reload_databases(_django_cursor_wrapper))


@pytest.fixture
def server_url(request, local_test):
    if local_test:
        return 'http://188.226.149.50/'
    live_server = request.getfuncargvalue('live_server')
    return live_server.url


@pytest.fixture
def selenium_driver(request, server_url, browser):
    driver = SeleniumWrapper(browser)
    driver.set_host(server_url)
    request.addfinalizer(driver.close)
    return driver
