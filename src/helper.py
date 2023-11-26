from src.modules import *

def findElement(driver, *keys, click=False):
    locator = data(*keys)
    element = driver.find_element(By.CSS_SELECTOR, locator)
    if click:
        element.click()
    else:
        return element
    
def findElements(driver, *keys, click=False):
    locator = data(*keys)
    element = driver.find_elements(By.CSS_SELECTOR, locator)
    if click:
        element.click()
    else:
        return element
    
def waitElement(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 60)
    element.until(EC.visibility_of_element_located(locator))
    return element
    
def waitElementInvis(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.invisibility_of_element(locator))

def wait_If_Clickable(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable(locator)
                ,message="\"Cannot find element\"")
    element.click()

def waitPresence(driver, *keys, text):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.text_to_be_present_in_element(locator, text_=text))
    return element

def waitElementPresence(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.presence_of_element_located(locator))
    return element

def closeBanner(driver):
    waitPresence(driver, 'marshall', 'banner', text='Close')
    driver.execute_script('return document.querySelector("div#banner-container").remove();')