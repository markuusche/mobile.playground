from src.modules import *
from . import GS_REPORT

def getToken():
    header = {}
    header['X-Operator'] = env('XOp')
    header['X-Key'] = env('Xkey')
    response = requests.get(env('base') + env('desc'), headers=header)
    return response.json()

def gameKey():
    fetch = getToken()
    username = {'username': env('username')}
    token = fetch['data']['token']
    header = {'X-token': token}
    response = requests.get(env('base') + env('key'), \
    params=username, headers=header)
    return response.json()['data']['key'], header

def getURL():
    key = gameKey()
    paramKey = {'key': key[0]}
    response = requests.get(env('base') + env('play'), \
    params=paramKey, headers=key[1])
    return response.json()['data']['url']

def addBalance(entry, amount):
    fetch = getToken()
    token = fetch['data']['token']
    header = {'X-token': token}
    body = {}
    body['username'] = env('username')
    body['balance'] = amount
    body['action'] = entry
    body['transferId'] = fake.passport_number()
    response = requests.post(env('base') + env('balance'), \
    headers=header, json=body)
    assert response.status_code == 200
    return response.json()['data']['balance']

# duplicate report format
def createNew_sheet():
    sheet, creds, date = gsheet_api()
    copy_sheet = sheet.worksheet('Report Format')
    spreadID = env('gsheetKey')
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

# send report to Google Sheet
def sendReport(sample, bet, tableDealer):
    rangeValue = []
    sheet, _, date = gsheet_api()
    sendReport = sheet.worksheet(f'Results of {date}')
    sendReport.update(range_name=f'{data('gsheet', bet)}', values=sample)
    
    getRange = re.findall(r'\d+', data('gsheet', bet))
    for i in getRange:
        rangeValue.append(i)
    
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

def gsheet_api():
    getCurrentDate = datetime.now(timezone.utc)
    dateFormat = getCurrentDate.strftime('%m/%d/%Y')
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    authcreds = gspread.authorize(creds)
    spreadsheet = authcreds.open_by_url(
    f'https://docs.google.com/spreadsheets/d/{env('gsheetKey')}/edit#gid=0')
    return spreadsheet, creds, dateFormat
