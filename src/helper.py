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
    wait = WebDriverWait(driver, 15)
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

def screenshot(driver, name, val):
    driver.save_screenshot(f'screenshots/{name} {val}.png')

def deleteScreenshots():
    path = 'screenshots/'
    files = os.listdir(path)
    for file_name in files:
        if file_name.endswith('.png'):
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    logs = 'logs.txt'
    if os.path.exists(logs):
        os.remove(logs)