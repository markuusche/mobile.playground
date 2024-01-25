import pytest
import yaml
import random
import requests
import pytest
import yaml
import os
import re
from time import sleep
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService

fake = Faker()

def data(*keys):
    with open('resources/locators.yaml','r') as file:
        getData = yaml.load(file, Loader=yaml.FullLoader)

    for key in keys:
        getData = getData[key]

    return getData

def phone():
    with open('resources/devices.yaml','r') as file:
        getData = yaml.load(file, Loader=yaml.FullLoader)
    return getData

def customJS(driver, function=None):
    with open(f'resources/script.js','r') as js:
        getScript = js.read()
        script = getScript + f'return {function}'
        run = driver.execute_script(script)
        return run

def driverJS(driver, script):
    return driver.execute_script(script)

def env(value:str):
    return os.environ.get(value)
