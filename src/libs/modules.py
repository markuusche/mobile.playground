import pytest
import yaml
import random
import requests
import yaml
import os
import platform
import re
import math
import cv2
import pytesseract
from time import sleep
from faker import Faker
from selenium import webdriver
import gspread
import uuid
import pytesseract as tess
import base64
import grapheme
import pyperclip
import traceback
from io import BytesIO
from PIL import Image
from .. import GS_REPORT
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime, timezone


deviceName = os.environ['USERPROFILE'].split(os.path.sep)[-1]
path = f'C:\\Users\\{deviceName}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
tess.pytesseract.tesseract_cmd = path

fake = Faker()
uuid = uuid.uuid1().hex
userAgent = UserAgent(platforms='mobile')

currDate = datetime.now()
date = currDate.strftime('%Y-%m-%d %H:%M')

class Tools:
    def data(self, *keys):
        with open('resources/source.yaml','r') as file:
            getData = yaml.load(file, Loader=yaml.FullLoader)

        for key in keys:
            getData = getData[key]

        return getData

    def phone(self):
        with open('resources/devices.yaml','r') as file:
            getData = yaml.load(file, Loader=yaml.FullLoader)
        return getData

    def customJS(self, driver, function=None):
        with open(f'resources/script.js','r') as js:
            getScript = js.read()
            script = getScript + f'return {function}'
            run = driver.execute_script(script)
            return run

    def driverJS(self, driver, script, element = 'auto'):
        return driver.execute_script(script, element)

    def env(self, value:str):
        return os.environ.get(value)
    
    def assertion(self, message, comparison=None, operator=None, comparison2=None, skip=False, notice=False):
        red = '\033[91m'
        green = '\033[32m'
        default = '\033[0m'
        yellow = '\033[93m'
        
        if notice:
            status = 'NOTICE'
            color = yellow
        else:
            status = 'PASSED'
            color = green
        
        if skip:
            print(f'{yellow}[ SKIPPED ]{default} {date} {message}')
            GS_REPORT.append(['SKIPPED'])
        else:
            try:
                if operator == '==':
                    assert comparison == comparison2
                elif operator == '!=':
                    assert comparison != comparison2
                elif operator == '>':
                    assert comparison > comparison2
                elif operator == '<':
                    assert comparison < comparison2
                elif operator == 'in':
                    assert comparison in comparison2
                else:
                    assert comparison
                
                print(f'{color}[ {status} ]{default} {date} {message}')
                if not notice:
                    GS_REPORT.append(['PASSED'])
            except AssertionError:
                print(f'{red}[ FAILED ]{default} {date} {message}')
                if not notice:
                    GS_REPORT.append(['FAILED'])