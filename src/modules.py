import pytest
import yaml
import random
import requests
import pytest
import yaml
import os
import re
import math
import cv2
import pytesseract
from time import sleep
from faker import Faker
from selenium import webdriver
import gspread
import cv2
import pytesseract as tess
import base64
import grapheme
import pyperclip
from io import BytesIO
from PIL import Image
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime, timezone

deviceName = os.environ['USERPROFILE'].split(os.path.sep)[-1]
path = f'C:\\Users\\{deviceName}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
tess.pytesseract.tesseract_cmd = path

fake = Faker()
userAgent = UserAgent(platforms='mobile')

def data(*keys):
    with open('resources/source.yaml','r') as file:
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

def driverJS(driver, script, element = 'auto'):
    return driver.execute_script(script, element)

def env(value:str):
    return os.environ.get(value)
