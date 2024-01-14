from src.modules import *
from src.api import *

# find the element <locator> source from locators.yaml
def findElement(driver, *keys, click=False):
    locator = data(*keys)
    element = driver.find_element(By.CSS_SELECTOR, locator)
    if click:
        element.click()
    else:
        return element

# find the elements <locator> source from locators.yaml
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
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 60)
    element.until(EC.visibility_of_element_located(locator))
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
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.text_to_be_present_in_element(locator, text_=text))
    return element

# waits for the elemennt to be present?
# (never used) for future reference
def waitElementPresence(driver, *keys):
    locator = (By.CSS_SELECTOR, data(*keys))
    element = WebDriverWait(driver, 600)
    element.until(EC.presence_of_all_elements_located(locator))
    return element

# exclusive function for closing ads
def closeBanner(driver):
    waitPresence(driver, 'marshall', 'banner', text='Close')
    driver.execute_script('return document.querySelector("div#banner-container").remove();')

# for digital message screenshots
def screenshot(driver, name, val, allin=False):
    if allin:
        driver.save_screenshot(f'screenshots/{name} {val}.png')

# delete all screenshots from screenshots/ folder
def deleteScreenshots():
    path = 'screenshots/'
    files = os.listdir(path)
    for file_name in files:
        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() in ['.png', '.PNG']:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

    logs = 'logs.txt'
    if os.path.exists(logs):
        os.remove(logs)

# reset coins to default amount when betting all-in. 
# for every table loop
def reset_coins(driver, game, amount):
    getBalance = addBalance(env('add'), amount)
    addBalance(env('deduc'), amount=getBalance)
    addBalance(env('add'), amount)
    driver.refresh()
    waitElement(driver, 'lobby', 'main')
    wait_If_Clickable(driver, 'category', game)
    elements = findElements(driver, 'lobby', game)
    return elements

