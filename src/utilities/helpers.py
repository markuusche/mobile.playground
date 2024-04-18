from src.libs.modules import *

# find single element <locator> source from locators.yaml
def findElement(driver, *keys, click=False, status=False):
    try:
        locator = data(*keys)
        element = driver.find_element(By.CSS_SELECTOR, locator)
        if click:
            element.click()
        else:
            return element
    except NoSuchElementException:
        if status:
            return False
        else:
            print(f'\033[91mFAILED No such element "{locator}" ')

# find multiple elements <locator> source from locators.yaml
def findElements(driver, *keys, click=False):
    locator = data(*keys)
    element = driver.find_elements(By.CSS_SELECTOR, locator)
    if click:
        element.click()
    else:
        return element
    
# waits an element from the <locator> source
# from locators.yaml to appear
def waitElement(driver, *keys, setTimeout=60):
    try:
        locator = (By.CSS_SELECTOR, data(*keys))
        element = WebDriverWait(driver, setTimeout)
        element.until(EC.visibility_of_element_located(locator))
    except:            
        print(f'Element did not appear {locator}')

    return element

# waits an element from the <locator> source
# from locators.yaml to disappear
def waitElementInvis(driver, *keys, setTimeout=600, isDigital=False, tableDealer=None):
    try:
        locator = (By.CSS_SELECTOR, data(*keys))
        element = WebDriverWait(driver, setTimeout)
        element.until(EC.invisibility_of_element(locator))
        if isDigital:
            print(f'\033[32mPASSED\033[0m [Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'New Round Digital Result is not displayed!')
    except:
        print(f'Element did not disappear {locator}')
        if isDigital:
            print(f'\033[91mFAILED\033[0m [Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'New Round Digital Result is displayed!')

# waits an element from the <locator> source
# from locator.yaml to disappear
def wait_If_Clickable(driver, *keys, setTimeout=15):
    locator = (By.CSS_SELECTOR, data(*keys))
    wait = WebDriverWait(driver, setTimeout)
    element = wait.until(EC.element_to_be_clickable(locator)
                ,message="\"Cannot find element\"")
    element.click()

# waits the presence of the element from the <locator> source
# from locator.yaml to appear
def waitPresence(driver, *keys, text, setTimeout=350, status=False):
    try:
        locator = (By.CSS_SELECTOR, data(*keys))
        element = WebDriverWait(driver, setTimeout)
        element.until(EC.text_to_be_present_in_element(locator, text_=text))
        return element
    except Exception:
        if status:
            return False
        else:
            print(f'\033[91mFAILED "{text}" was not captured by selenium.')
