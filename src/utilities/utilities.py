from src.libs.modules import *
from src.utilities.helpers import Helpers

class Utilities(Helpers):
    def __init__(self) -> None:
        super().__init__()
    
    def screenshot(self, driver, name, val, allin=False):
        if allin:
            driver.save_screenshot(f'screenshots/{name} {val}.png')

    def debuggerMsg(self, tableDealer, str="", str2=""):
        return f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'{str} {str2}'

    def deleteImages(self, folder, logs=False):
        path = f'{folder}\\'
        files = os.listdir(path)
        for file in files:
            pathFile = os.path.join(path, file)
            if os.path.isfile(pathFile):
                os.remove(pathFile)

        if logs:
            logpath = 'logs\\'
            txt = os.listdir(logpath)
            for log in txt:
                truePath = os.path.join(logpath, log)
                if os.path.exists(truePath):
                    os.remove(truePath)

    def disableStream(self, driver, stream):
        if not stream:
            toggled = self.findElement(driver, 'in-game', 'video-toggled')
            isToggled = toggled.get_attribute('class')
            while 'toggled' in isToggled:
                self.customJS(driver, f'click("{self.data("in-game", "close-video")}");')
                stream = True
                break
            
    def table_dealer(self, driver):
        """
        retrieve the table number and dealer information.

        params:
        `driver` (webdriver): the selenium webdriver instance.

        find and return the table number and dealer's name.
        """
        tableNumber = self.findElement(driver, 'in-game', 'tableNumber')
        dealer = self.findElement(driver, 'in-game', 'dealer')
        return tableNumber.text, dealer.text

    def skipOnFail(self, driver, tableDealer, exception):
        """
        Skip the current test case upon encountering an exception, refresh the driver, and clear the GS_REPORT.
        
        params:
        `driver` (webdriver): The Selenium WebDriver instance.
        `tableDealer` (string): A string containing information about the table and dealer.
        `exception` (exception: The exception raised during the test execution.

        : This function is designed to handle test case failures gracefully by logging the exception details and 
        : traceback information to a file. It then refreshes the WebDriver instance, clears any existing report data, 
        : and waits for the 'lobby' and 'main' elements to be available before proceeding.  
        : It extracts the exception message and traceback, appends them to a log file named 'tracelogs.txt' with 
        : information about the table and dealer, and separates each log entry with a newline for clarity.
        """
        
        message = self.debuggerMsg(tableDealer, f'---- SKIPPED ----')
        self.assertion(message, notice=True)
        driver.refresh()
        self.waitElement(driver, 'lobby', 'main')
        print('=' * 100)
        GS_REPORT.clear()
        
        exc = str(exception).split('Stacktrace:')[0].strip()
        tb = traceback.format_exc().split('Stacktrace:')[0].strip()

        with open('logs\\tracelogs.txt','a') as logs:
            logs.write(f'Table: {tableDealer[0]} Dealer: {tableDealer[1]} \n {exc} \n'\
            f'\nTraceback: {tb} \n\n')