from .. import GS_REPORT
from src.libs.modules import Tools
from src.utilities.helpers import *

class Requests(Tools):
    def getToken(self):
        header = {}
        header[self.env('Ops')] = self.env('XOp')
        header[self.env('querKey')] = self.env('Xkey')
        response = requests.get(self.env('base') + self.env('desc'), headers=header)
        return response.json()

    def gameKey(self):
        fetch = self.getToken()
        username = {'username': self.env('username'), f'{self.env("bl")}': 124}
        token = fetch['data']['token']
        header = {self.env('tk'): token}
        response = requests.get(self.env('base') + self.env('key'), \
        params=username, headers=header)
        return response.json()['data']['key'], header

    def getURL(self):
        key = self.gameKey()
        paramKey = {'key': key[0]}
        response = requests.get(self.env('base') + self.env('play'), \
        params=paramKey, headers=key[1])
        return response.json()['data']['url']

    def addBalance(self, entry, amount):
        fetch = self.getToken()
        token = fetch['data']['token']
        header = {self.env('tk'): token}
        body = {}
        body['username'] = self.env('username')
        body['balance'] = amount
        body['action'] = entry
        body['transferId'] = fake.passport_number()
        response = requests.post(self.env('base') + self.env('balance'), \
        headers=header, json=body)
        assert response.status_code == 200
        return response.json()['data']['balance']

    # duplicate report format
    def createNew_sheet(self, driver):
        sheet, creds, date = self.gsheet_api()
        copy_sheet = sheet.worksheet('Report Format')
        spreadID = self.env('gsheetKey')
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

    # send report to Google Sheet
    def sendReport(self, sample, bet, tableDealer):
        rangeValue = []
        sheet, _, date = self.gsheet_api()
        sendReport = sheet.worksheet(f'Results of {date}')
        sendReport.update(range_name=f"{self.data('gsheet', bet)}", values=sample)
        
        getRange = re.findall(r'\d+', self.data('gsheet', bet))
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

    def gsheet_api(self):
        getCurrentDate = datetime.now(timezone.utc)
        dateFormat = getCurrentDate.strftime('%m/%d/%Y')
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.env('acss'), scope)
        authcreds = gspread.authorize(creds)
        spreadsheet = authcreds.open_by_url(
        f'https://docs.google.com/spreadsheets/d/{self.env("gsheetKey")}/edit#gid=0')
        return spreadsheet, creds, dateFormat
