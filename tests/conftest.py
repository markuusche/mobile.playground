from src.modules import *
from src.functions import *

def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False)
    parser.addoption("--gsreport", action="store_true", default=False)

@pytest.fixture(scope='session')
def headless(request):
    return request.config.getoption("headless")

@pytest.fixture(scope='session')
def gsreport(request):
    return request.config.getoption("gsreport")

@pytest.fixture(scope='session')
def driver(headless):
    #setup
    option = webdriver.EdgeOptions()
    option.add_argument("--hide-scrollbars")

    if headless:
        option.add_argument("--headless=new")

    option.add_argument("--incognito")
    option.add_argument("--mute-audio")
    option.add_argument("---disk-cache-dir=nul")
    option.add_argument("--disable-features=msEdgeEnableNurturingFramework")
    option.add_argument("window-position=1410,0")
    option.add_argument("window-size=446,972")
    option.add_experimental_option("mobileEmulation", emulation())
    option.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Edge(options=option)
    driver.get(getURL())

    yield driver
    
    #teardown
    driver.close()
    driver.quit()

@pytest.fixture
def lobby(request, driver):
  yield
  if request.session.testsfailed:
    driver.refresh()

def emulation():
    return {
        "deviceMetrics": {
            "width": 430, 
            "height": 932, 
            "pixelRatio": 3.0
            },
        "userAgent": 'Mozilla/5.0'\
        '(Linux; Android 14.0; iPhone 14 Pro Max/MRA58N)'\
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85'\
        'Mobile Safari/537.36'
    }

