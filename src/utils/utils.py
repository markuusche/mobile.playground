import os
import yaml

from .. import GS_REPORT
from datetime import datetime

class Utilities:
    
    def screenshot(self, driver, name, val, allin=False):
        if allin:
            driver.save_screenshot(f'screenshots/{name} {val}.png')

    def debuggerMsg(self, tableDealer, msg="", msg2=""):
        return f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'{msg} {msg2}'

    def deleteImages(self, folder, logs=False):
        path = folder
        files = os.listdir(path)
        for file in files:
            pathFile = os.path.join(path, file)
            if os.path.isfile(pathFile):
                os.remove(pathFile)

        if logs:
            logpath = 'logs'
            txt = os.listdir(logpath)
            for log in txt:
                truePath = os.path.join(logpath, log)
                if os.path.exists(truePath):
                    os.remove(truePath)

    def data(self, *keys):
        with open('resources/source.yaml','r') as file:
            getData = yaml.load(file, Loader=yaml.FullLoader)

        for key in keys:
            getData = getData[key]

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
    
    def _getdate(self):
        currDate = datetime.now()
        date = currDate.strftime('%H:%M')
        return date
    
    def assertion(self, message, actual=None, operator=None, expected=None, skip=False, notice=False):
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
            print(f'{yellow}[ SKIPPED ]{default} {self._getdate()} {message}')
            GS_REPORT.append(['SKIPPED'])
        else:
            try:
                if operator == '==':
                    assert actual == expected
                elif operator == '!=':
                    assert actual != expected
                elif operator == '>':
                    assert actual > expected
                elif operator == '<':
                    assert actual < expected
                elif operator == 'in':
                    assert actual in expected
                else:
                    assert actual
                
                print(f'{color}[ {status} ]{default} {self._getdate()} {message}')
                if not notice:
                    GS_REPORT.append(['PASSED'])
            except AssertionError:
                print(f'{red}[ FAILED ]{default} {self._getdate()} {message}')
                if not notice:
                    GS_REPORT.append(['FAILED'])
