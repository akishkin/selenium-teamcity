from selenium import webdriver
from django.conf import settings

class SeleniumWrapper:

    authorized = False

    base_url = "http://python.org"

    def __init__(self, driver = "Firefox"):
        self._driver = webdriver.Firefox()
        # self._driver = webdriver.Chrome(settings.PROJECT_ROOT+'/../selenium_tests/chromedriver/chromedriver')

    def set_host(self, host):
        self.base_url = host

    def get_driver(self):
        return self._driver

    def close(self):
        self._driver.close()