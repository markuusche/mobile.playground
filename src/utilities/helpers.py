from src.libs.modules import *

class Helpers(Tools):

    def __init__(self) -> None:
        super().__init__()

    # find single element <locator> source from locators.yaml
    def findElement(self, driver, *keys, click=False, status=False):
        try:
            locator = self.data(*keys)
            element = driver.find_element(By.CSS_SELECTOR, locator)
            if click:
                element.click()
            else:
                return element
        except NoSuchElementException:
            if status:
                return False
            else:
                print(f'\033[91m[ FAILED ] No such element "{locator}" ')

    # find multiple elements <locator> source from locators.yaml
    def findElements(self, driver, *keys, click=False):
        locator = self.data(*keys)
        element = driver.find_elements(By.CSS_SELECTOR, locator)
        if click:
            element.click()
        else:
            return element

    # waits an element from the <locator> source
    # from locators.yaml to appear
    def waitElement(self, driver, *keys, setTimeout=60):
        try:
            locator = (By.CSS_SELECTOR, self.data(*keys))
            element = WebDriverWait(driver, setTimeout)
            element.until(EC.visibility_of_element_located(locator))
        except:
            print(f'Element did not appear {locator}')

        return element

    # waits an element from the <locator> source
    # from locators.yaml to disappear
    def waitElementInvis(self, driver, *keys, setTimeout=600, isDigital=False, tableDealer=None):
        try:
            locator = (By.CSS_SELECTOR, self.data(*keys))
            element = WebDriverWait(driver, setTimeout)
            element.until(EC.invisibility_of_element(locator))
            if isDigital:
                print(f'\033[32m[ PASSED ]\033[0m {self._getdate()} [Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                f'New Round Digital Result is not displayed!')
        except:
            print(f'Element did not disappear {locator}')
            if isDigital:
                print(f'\033[91m[ FAILED ]\033[0m {self._getdate()} [Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                f'New Round Digital Result is displayed!')

    # waits an element from the <locator> source
    # from locator.yaml to disappear
    def wait_If_Clickable(self, driver, *keys, setTimeout=15):
        locator = (By.CSS_SELECTOR, self.data(*keys))
        wait = WebDriverWait(driver, setTimeout)
        element = wait.until(EC.element_to_be_clickable(locator)
                    ,message="\"Cannot find element\"")
        element.click()

    # waits the presence of the element from the <locator> source
    # from locator.yaml to appear
    def waitPresence(self, driver, *keys, text, setTimeout=350, status=False):
        try:
            locator = (By.CSS_SELECTOR, self.data(*keys))
            element = WebDriverWait(driver, setTimeout)
            element.until(EC.text_to_be_present_in_element(locator, text_=text))
            return element
        except Exception:
            if status:
                return False
            else:
                print(f'\033[91m[ FAILED ] {self._getdate()} "{text}" was not captured by selenium.')
