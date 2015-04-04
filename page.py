# coding: utf-8

class MainPage(BasePage):

    def load(self):
        self.go_to("/")
        self._expected_title = u"Python"

    def is_results_found(self):
        return "No results found." not in self.driver.page_source

    def search(self, query):
        self.fill_textfield(MainPageLocators.QUERY, query)
        self.click(MainPageLocators.GO_BUTTON)