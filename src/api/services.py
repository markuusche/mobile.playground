import re
import time
import json, uuid
import requests
import gspread

from faker import Faker
from .. import GS_REPORT
from src.api.hash import Signature
from src.utils.utils import Utilities
from datetime import datetime, timezone
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

class Services:

    def __init__(self) -> None:
        self.generate = Signature()
        self.utils = Utilities()
        self.faker = Faker()
        self.uuid = uuid.uuid1().hex
        self.timestamp = int(time.time())
        self.base = self.utils.env('base')
        self.username = self.utils.env('username')
        self.headers = json.loads(self.utils.env('headers'))

    def GET_GAME_URL(self):
        getParams = json.loads(self.utils.env('data_URL'))
        getParams['player_id'] = self.username
        getParams['timestamp'] = f"{self.timestamp}"
        params = self.generate.signature(getParams)
        getParams['signature'] = params
        response = requests.get(self.base + self.utils.env('play'), \
        params=getParams, headers=self.headers)
        return response.json()['game_link']

    def GET_BALANCE(self):
        params = {'player_id': self.username}
        response = requests.get(self.base + self.utils.env('balance'), \
        params=params, headers=self.headers)
        return response.json()['current_balance']

    def POST_ADD_BALANCE(self, amount):
        currBalance = self.GET_BALANCE()
        
        def body(amount):
            body = {}
            body['player_id'] = self.username
            body[self.utils.env('tr')] = self.utils.getUuid(True)
            body[self.utils.env('tra')] = amount
            body['timestamp'] = f'{self.timestamp}'
            data = self.generate.signature(body)
            body['signature'] = data
            return body
        
        getBody = body(currBalance)
        requests.post(self.base + self.utils.env('deduc'), \
        json=getBody, headers=self.headers)
        
        getBody = body(amount)
        requests.post(self.base + self.utils.env('add'), \
        json=getBody, headers=self.headers)
    
    def CREATE_GSHEET(self, driver):
        sheet, creds, date = self.GSHEET_API()
        copy_sheet = sheet.worksheet('Report Format')
        spreadID = self.utils.env('gsheetKey')
        getsheetID = copy_sheet.id
        service = build('sheets', 'v4', credentials=creds)

        checkNameExist = sheet.worksheets()
        sheetName = [worksheet.title for worksheet in checkNameExist]
        newName = f'Results of {date}'
        if newName not in sheetName:
            sendRequest = {
                "duplicateSheet":{
                    "sourceSheetId": getsheetID,
                    "insertSheetIndex": 0,
                    "newSheetName": newName
                }
            }

            service.spreadsheets().batchUpdate(spreadsheetId=spreadID,\
            body={'requests': [sendRequest]}).execute()
            sendReport = sheet.worksheet(f'Results of {date}')
            getVersion = self.utils.customJS(driver, 'currVersion();')
            version = [[f'v{getVersion}']]
            sendReport.update(range_name='B5:F5', values=version)
            
    def SEND_REPORT(self, sample, bet, tableDealer):
        rangeValue = []
        sheet, _, date = self.GSHEET_API()
        sendReport = sheet.worksheet(f'Results of {date}')
        sendReport.update(range_name=f"{self.utils.data('gsheet', bet)}", values=sample)

        getRange = re.findall(r'\d+', self.utils.data('gsheet', bet))
        for cell in getRange:
            rangeValue.append(cell)

        for row in range(int(rangeValue[0]), int(rangeValue[1]) + 1):
            getValue = sendReport.cell(row, 4).value
            if getValue == 'FAILED':
                getValue = sendReport.cell(row, 5).value
                if getValue not in [None, '']:
                    updateCell = getValue + ", " + str(tableDealer[0])
                else:
                    updateCell = str(tableDealer[0])

                sendReport.update_cell(row, 5, updateCell)

        GS_REPORT.clear()
        
    def GSHEET_API(self):
        getCurrentDate = datetime.now(timezone.utc)
        dateFormat = getCurrentDate.strftime('%m/%d/%Y')
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.utils.env('acss'), scope)
        authcreds = gspread.authorize(creds)
        spreadsheet = authcreds.open_by_url(
        f'https://docs.google.com/spreadsheets/d/{self.utils.env("gsheetKey")}/edit#gid=0')
        return spreadsheet, creds, dateFormat