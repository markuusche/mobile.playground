from src.modules import *
from src.api import *

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

# for digital message screenshots
def captureDigitalMessage(driver, value, count, allin=False):
    if allin:
        screenshot(driver , value, count)

# delete all screenshots
def removePNGs(path):
    files = os.listdir(path)
    for file_name in files:
        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() in ['.png', '.PNG']:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

def deleteScreenshots():
    removePNGs('screenshots/')
    removePNGs('screenshots/card results/')

    logs = 'logs.txt'
    if os.path.exists(logs):
        print(f"Deleting logs file: {logs}")
        os.remove(logs)


# reset coins to default when betting all-in. 
# -this is per table loop-
def reset_coins(driver, game):
    getBalance = addBalance(env('add'))
    addBalance(env('deduc'), amount=getBalance)
    addBalance(env('add'))
    driver.refresh()
    waitElement(driver, 'lobby', 'content')
    #closeBanner(driver)
    sleep(2)
    findElement(driver, 'category', game, click=True)
    elements = findElements(driver, 'lobby', game)
    return elements
