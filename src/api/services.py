import re
import requests
import gspread

from faker import Faker
from .. import GS_REPORT
from src.utils.utils import Utilities
from datetime import datetime, timezone
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

class Services():

    def __init__(self) -> None:
        self.utils = Utilities()
        self.faker = Faker()

    def GET_Token(self):
        header = {}
        header[self.utils.env('Ops')] = self.utils.env('XOp')
        header[self.utils.env('querKey')] = self.utils.env('Xkey')
        response = requests.get(self.utils.env('base') + self.utils.env('desc'), headers=header)
        return response.json()
    
    def GET_Key(self):
        fetch = self.GET_Token()
        username = {'username': self.utils.env('username'), f'{self.utils.env("bl")}': 124}
        token = fetch['data']['token']
        header = {self.utils.env('tk'): token}
        response = requests.get(self.utils.env('base') + self.utils.env('key'), \
        params=username, headers=header)
        return response.json()['data']['key'], header

    def GET_URL(self):
        key = self.GET_Key()
        paramKey = {'key': key[0]}
        response = requests.get(self.utils.env('base') + self.utils.env('play'), \
        params=paramKey, headers=key[1])
        return response.json()['data']['url']
    
    def POST_ADD_BALANCE(self, entry, amount):
        fetch = self.GET_Token()
        token = fetch['data']['token']
        header = {self.utils.env('tk'): token}
        body = {}
        body['username'] = self.utils.env('username')
        body['balance'] = amount
        body['action'] = entry
        body['transferId'] = self.faker.passport_number()
        response = requests.post(self.utils.env('base') + self.utils.env('balance'), \
        headers=header, json=body)
        assert response.status_code == 200
        return response.json()['data']['balance']
    
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
            getVersion = self.customJS(driver, 'currVersion();')
            version = [[f'VERSION: {getVersion}']]
            sendReport.update(range_name='B5:E5', values=version)
            
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