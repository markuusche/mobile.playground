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

    option.add_argument("--InPrivate")
    option.add_argument("--mute-audio")
    option.add_argument("---disk-cache-dir=nul")
    option.add_argument("--disable-features=msEdgeEnableNurturingFramework")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("window-position=910,0")
    option.add_argument("window-size=375,770")
    option.add_argument(f"--user-agent=")
    option.add_argument(f"--app={getURL()}")
    option.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Edge(options=option)

    yield driver
        
    #teardown
    driver.close()
    driver.quit()

@pytest.fixture
def lobby(request, driver):
  yield
  if request.session.testsfailed:
    driver.refresh()
