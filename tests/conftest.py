from src.modules import *
from src.api import *
from src.helpers import *

def pytest_addoption(parser):
    parser.addoption("--device", action="store", default=None)
    parser.addoption("--headless", action="store_true", default=False)
    parser.addoption("--noimage", action="store_true", default=False)

@pytest.fixture(scope='session')
def device(request):
    return request.config.getoption("device")

@pytest.fixture(scope='session')
def headless(request):
    return request.config.getoption("headless")

@pytest.fixture(scope='session')
def noimage(request):
    return request.config.getoption("noimage")

@pytest.fixture(scope='session')
def driver(device, headless, noimage):
    #setup
    deleteScreenshots()
    URL = play()
    option = Options()
    option.add_argument("--hide-scrollbars")

    if headless:
        option.add_argument("--headless=new")

    if noimage:
        option.add_argument("--blink-settings=imagesEnabled=false")

    option.add_argument("--disable-gpu")
    option.add_argument("--incognito")
    option.add_argument("--mute-audio")
    devices = phone()['deviceName']
    getRandom = random.choice(devices)

    if device:
        option.add_experimental_option("mobileEmulation", {"deviceName": device})
    else:
        option.add_experimental_option("mobileEmulation", {"deviceName": getRandom})

    driver = webdriver.Chrome(options=option)
    driver.get(URL)
    yield driver
    #teardown
    driver.close()
    driver.quit()

@pytest.fixture
def lobby(request, driver):
  yield
  if request.session.testsfailed:
    driver.refresh()