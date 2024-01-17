from src.modules import *
from src.api import *
from src.helpers import *

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
def driver(device, headless):
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
    devices = phone()['deviceName']
    getRandom = random.choice(devices)

    if device:
        option.add_experimental_option("mobileEmulation", {"deviceName": device})
    else:
        option.add_experimental_option("mobileEmulation", {"deviceName": getRandom})
        print(f'Device used to run: {getRandom}')

    driver = webdriver.Chrome(options=option)
    driver.get(URL)
    yield driver
    #teardown
    driver.quit()

@pytest.fixture
def lobby(request, driver):
  yield
  if request.session.testsfailed:
    driver.refresh()