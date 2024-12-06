import traceback
from .. import GS_REPORT
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.utils import Utilities

class Helpers:

    def __init__(self) -> None:
        self.utils = Utilities()
    
    def search_element(self, driver, *keys, click=False, status=False):
        try:
            locator = self.utils.data(*keys)
            element = driver.find_element(By.CSS_SELECTOR, locator)
            
            if click:
                element.click()
            else:
                return element
        except NoSuchElementException:
            if status:
                return False
            else:
                print(f'\033[91m[ FAILED ] "{locator}" element not found or does not exist.')
    
    def search_elements(self, driver, *keys):
        try:
            locator = self.utils.data(*keys)
            element = driver.find_elements(By.CSS_SELECTOR, locator)
            return element
        except:
            print(f'\033[91m[ FAILED ] "{locator}" elements not found or does not exist.')
    
    def wait_element(self, driver, *keys, timeout=60):
        try:
            locator = (By.CSS_SELECTOR, self.utils.data(*keys))
            element = WebDriverWait(driver, timeout)
            element.until(EC.visibility_of_element_located(locator))
        except:
            print(f'\033[91m[ FAILED ] "{locator}" element was not displayed.')
    
    def wait_element_invisibility(self, driver, *keys, absolute=False, timeout=600):
        try:
            locator = (By.CSS_SELECTOR, self.utils.data(*keys))
            element = WebDriverWait(driver, timeout)
            if absolute:
                element.until(EC.invisibility_of_element_located(locator))
            else:  
                element.until(EC.invisibility_of_element(locator))
        except:
            print(f'\033[91m[ FAILED ] "{locator}" element still diplayed.')
        
    def wait_clickable(self, driver, *keys, timeout=15):
        locator = (By.CSS_SELECTOR, self.utils.data(*keys))
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.element_to_be_clickable(locator),
        message=f'\033[91m[ FAILED ] "{locator}" element was not clickable.')
        element.click()
        
    def wait_text_element(self, driver, *keys, text, timeout=350, status=False):
        try:
            locator = (By.CSS_SELECTOR, self.utils.data(*keys))
            element = WebDriverWait(driver, timeout)
            element.until(EC.text_to_be_present_in_element(locator, text_=text))
            return element
        except:
            if status:
                return False
            else:
                print(f'\033[91m[ FAILED ] "{locator}" cannot locate text in the element.')
                
    def disableStream(self, driver, stream):
        if not stream:
            toggled = self.search_element(driver, 'in-game', 'video-toggled')
            isToggled = toggled.get_attribute('class')
            while 'toggled' in isToggled:
                self.utils.customJS(driver, f'click("{self.utils.data("in-game", "close-video")}");')
                stream = True
                break
    
    def table_dealer(self, driver):
        """
        retrieve the table number and dealer information.

        params:
        `driver` (webdriver): the selenium webdriver instance.

        find and return the table number and dealer's name.
        """
        tableNumber = self.search_element(driver, 'in-game', 'tableNumber')
        dealer = self.search_element(driver, 'in-game', 'dealer')
        return tableNumber.text, dealer.text

    def skipOnFail(self, driver, exception):
        """
        Skip the current test case upon encountering an exception, refresh the driver, and clear the GS_REPORT.

        params:
        `driver` (webdriver): The Selenium WebDriver instance.
        `tableDealer` (string): A string containing information about the table and dealer.
        `exception` (exception: The exception raised during the test execution.

        : This function is designed to handle test case failures gracefully by logging the exception details and
        : traceback information to a file. It then refreshes the WebDriver instance, clears any existing report data,
        : and waits for the 'lobby' and 'main' elements to be available before proceeding.
        : It extracts the exception message and traceback, appends them to a log file named 'tracelogs.txt' with
        : information about the table and dealer, and separates each log entry with a newline for clarity.
        """
        tableDealer = self.table_dealer(driver)
        message = self.utils.debuggerMsg(tableDealer, f'---- SKIPPING TABLE ----')
        self.utils.assertion(message, notice=True)
        driver.refresh()
        self.wait_element(driver, 'lobby', 'main')
        print('=' * 100)
        GS_REPORT.clear()

        exc = str(exception).split('Stacktrace:')[0].strip()
        tb = traceback.format_exc().split('Stacktrace:')[0].strip()

        with open('logs\\tracelogs.txt','a') as logs:
            logs.write(f'Table: {tableDealer[0]} Dealer: {tableDealer[1]} \n {exc} \n'\
            f'\nTraceback: {tb} \n\n')