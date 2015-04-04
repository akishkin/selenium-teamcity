# coding: utf-8
import random

from locators import *
from page import *


class TestSelenium(object):

    def test_main_page(self, selenium_driver):
        main_page = MainPage(selenium_driver)
        assert main_page.check_title() is True

        main_page.search('pycon')
        assert main_page.is_results_found()


