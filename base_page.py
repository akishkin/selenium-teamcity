# coding: utf-8

from locators import *

class BasePage(object):

    _expected_title = ""

    def __init__(self, selenium_driver):
        self.driver = selenium_driver.get_driver()
        self.base_url = selenium_driver.base_url
        self.load()

    def go_to(self, url):
        self.driver.get(self.base_url + url)

    def fill_textfield(self, element, text):
        elem = self.driver.find_element(*element)
        elem.clear()
        elem.send_keys(text)

    def click(self, element):
        elem = self.driver.find_element(*element)
        elem.click()

    def check_title(self, title=''):
        if title == '':
            return self._expected_title in self.driver.title

        else:
            return title in self.driver.title
