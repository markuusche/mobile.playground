import pytest
from selenium import webdriver
from src.api.services import Services
from fake_useragent import UserAgent
userAgent = UserAgent(platforms='mobile')

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
    URL = Services()
    option = webdriver.ChromeOptions()
    option.add_argument("--hide-scrollbars")

    if headless:
        option.add_argument("--headless=new")

    option.add_argument("--incognito")
    option.add_argument("--mute-audio")
    option.add_argument("---disk-cache-dir=nul")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("window-position=1490,0")
    option.add_argument("window-size=440,840")
    option.add_argument(f"--user-agent={userAgent.random}")
    option.add_argument(f"--app={URL.GET_URL()}")
    option.add_experimental_option("excludeSwitches",["enable-automation"])
    driver = webdriver.Chrome(options=option)

    yield driver
        
    #teardown
    driver.close()
    driver.quit()

#disable logging
def traceLog_Handler(call, report):
    if call.excinfo is not None:
        if report.failed:
            report.longrepr = None