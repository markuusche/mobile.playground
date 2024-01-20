from src.modules import *
from src.functions import *

def pytest_addoption(parser):
    parser.addoption("--device", action="store", default=None)
    parser.addoption("--headless", action="store_true", default=False)

@pytest.fixture(scope='session')
def device(request):
    return request.config.getoption("device")

@pytest.fixture(scope='session')
def headless(request):
    return request.config.getoption("headless")

@pytest.fixture(scope='session')
def driver(headless):
    #setup
    deleteScreenshots()
    URL = play()
    option = Options()
    option.add_argument("--hide-scrollbars")

    if headless:
        option.add_argument("--headless=new")

    option.add_argument("--disable-popup-blocking")
    option.add_argument("--disable-default-apps ")
    option.add_argument("--incognito")
    option.add_argument("--mute-audio")
    option.add_experimental_option("mobileEmulation", emulation())

    driver = webdriver.Chrome(options=option)
    driver.set_window_size(425, 1065)
    driver.get(URL)

    yield driver
    
    #teardown
    driver.quit()

@pytest.fixture
def lobby(request, driver):
  yield
  if request.session.testsfailed:
    driver.refresh()

def emulation():
    return {
        "deviceMetrics": {
            "width": 500, 
            "height": 930, 
            "pixelRatio": 3.0
            },
        "userAgent": 'Mozilla/5.0'\
        '(Linux; Android 14.0; Samsung Galaxy S20 Ultra/MRA58N)'\
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97'\
        'Mobile Safari/537.36'
    }
