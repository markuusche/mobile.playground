from src.modules import *

# find single element <locator> source from locators.yaml
def findElement(driver, *keys, click=False):
    locator = data(*keys)
    element = driver.find_element(By.CSS_SELECTOR, locator)
    if click:
        element.click()
    else:
        return element

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
def waitElement(driver, *keys):
    try:
        locator = (By.CSS_SELECTOR, data(*keys))
        element = WebDriverWait(driver, 60)
        element.until(EC.visibility_of_element_located(locator))
    except:
        driver.save_screenshot(f'screenshots/Timedout.png')

    return element

# waits an element from the <locator> source
# from locators.yaml to disappear
def waitElementInvis(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.invisibility_of_element(locator))

# waits an element from the <locator> source
# from locator.yaml to disappear
def wait_If_Clickable(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    wait = WebDriverWait(driver, 15)
    element = wait.until(EC.element_to_be_clickable(locator)
                ,message="\"Cannot find element\"")
    element.click()

# waits the presence of the element from the <locator> source
# from locator.yaml to appear
def waitPresence(driver, *keys, text):
    try:
        locator = (By.CSS_SELECTOR, data(*keys))
        element = WebDriverWait(driver, 600)
        element.until(EC.text_to_be_present_in_element(locator, text_=text))
        return element
    except TimeoutException:
        print(f'{text} did not appeared or not displayed.')

# waits for the elemennt to be present?
# (never used) for future reference
def waitElementPresence(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.presence_of_all_elements_located(locator))
    return element
