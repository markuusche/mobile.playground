from src.modules import *
from src.helpers import *
from src.api import *
from . import GS_REPORT

# for digital message screenshots
def screenshot(driver, name, val, allin=False):
    if allin:
        driver.save_screenshot(f'screenshots/{name} {val}.png')

def debuggerMsg(tableDealer, str="", str2=""):
    return f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
        f'{str} {str2}'

# delete all screenshots from screenshots/ folder
def deleteScreenshots():
    path = 'screenshots/'
    files = os.listdir(path)
    for file_name in files:
        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() in ['.png', '.PNG']:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

# reset coins to default amount when betting all-in. 
# for every table loop
def reset_coins(driver, game, amount):
    try: # catching error to prevent blank lobby after a long run
        getBalance = addBalance(env('add'), amount)
        addBalance(env('deduc'), amount=getBalance)
        addBalance(env('add'), amount)
        driver.get(getURL())    
        waitElement(driver, 'lobby', 'main')
        wait_If_Clickable(driver, 'category', game)
        elements = findElements(driver, 'lobby', 'table panel')
        return elements
    except:
        # catch here -> refresh token and browser
        driver.get(getURL())

# check if the player balance from top left panel icon
# and in the middle panel matches.
def checkPlayerBalance(driver, game):
    if game != 'roulette':
        tableDealer = table_dealer(driver)
        coins = findElement(driver, 'in-game', 'balance')
        playerBalance = findElement(driver, 'in-game', 'playerBalance')
        message = debuggerMsg(tableDealer, f'Top balance {coins.text} & '\
        f'Bottom balance {playerBalance.text} - Expected: EQUAL')
        assertion(message, coins.text, '==', playerBalance.text)

# gets Lose or Win message with the values
def LoseOrWin(driver):
    waitElement(driver, 'in-game', 'resultToast')
    result = findElement(driver, 'in-game', 'winloss')
    if '-' in result.text:
        getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
        return f'Lose: {getText:.2f}'
    else:
        getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
        return f'Win: {getText:.2f}'
    
def cancelAssert(driver, tableDealer, allin, texts):
    wait_If_Clickable(driver, 'action', 'cancel')
    screenshot(driver, texts, tableDealer[0], allin)
    sumBetPlaced(driver, tableDealer, cancel=True, text=texts)

def betting(driver, betArea, game, placeConfirm=False):
    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
    loopRange = 10 if game in ['sicbo', 'roulette'] else len(betArea)
    i = 0
    while i < loopRange:
        index = random.choice(range(len(betArea)))
        try:
            wait_If_Clickable(driver, game, betArea[index])
            if placeConfirm:
                wait_If_Clickable(driver, 'action', 'confirm')

            i += 1
        except ElementClickInterceptedException:
            break

def getChipValue(driver):
    chips = 0.00
    placed_chips = findElements(driver, 'in-game', 'totalMoney')

    for i in placed_chips:
        if i.text != '':
            chips += float(i.text.replace(',',''))
    
    return chips

# cancel and then rebet test case
def cancelRebet(driver, betArea, tableDealer, game, allin=False):
    numbers = editChips(driver, 20)
    betting(driver, betArea, game)
    chips = getChipValue(driver)
    message = debuggerMsg(tableDealer, '\033[93mChips are being placed.') 
    assertion(message, chips, '>', numbers, notice=True)

    cancelAssert(driver, tableDealer, allin, 'Chip placed & cancelled!')
    betting(driver, betArea, game, placeConfirm=True)
    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
    wait_If_Clickable(driver, 'action', 'rebet')

    insufficient = customJS(driver, 'toast_check("Insufficient funds to rebet!");')
    message = debuggerMsg(tableDealer, 'Insufficient funds to rebet! Unable to Rebet and Cancel')
    if insufficient:
        assertion(message, skip=True)
    else:
        cancelAssert(driver, tableDealer, allin, 'Rebet & Cancelled!')
        wait_If_Clickable(driver, 'action', 'rebet')
        wait_If_Clickable(driver, 'action', 'confirm')
        screenshot(driver, 'Rebet & Confirmed!', tableDealer[0], allin)
        waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

# edit chips from in-game
def editChips(driver, divideBy=10):
    bets = findElement(driver, 'in-game', 'balance')
    value = float(bets.text.replace(',',''))
    chips = int(value) / divideBy
    if chips > 9:
        wait_If_Clickable(driver, 'in-game', 'edit')
        waitElement(driver, 'in-game', 'chip amount')
        wait_If_Clickable(driver, 'in-game', 'edit button')
        wait_If_Clickable(driver, 'in-game', 'clear')
        input = findElement(driver, 'in-game', 'input chips')
        input.send_keys(int(chips))
        wait_If_Clickable(driver, 'in-game', 'save amount')
        wait_If_Clickable(driver, 'in-game', 'payrate-close')
        return chips

# Bet all coins until Insufficient funds message appear
def coins_allin(driver, game, allin=False):
    global s6

    coins = findElement(driver, 'in-game','balance')
    tableDealer = table_dealer(driver)
    bet_areas = list(data(game))
    s6 = random.choice(range(0, 2))

    cancelRebet(driver, bet_areas, tableDealer, game, allin=True)
    editChips(driver, 10)

    if s6 == 1 and game == 'baccarat':
        wait_If_Clickable(driver, 'super6', 'r-area')
        waitElement(driver, 'super6', 's6')
        wait_If_Clickable(driver, 'super6', 's6')

    for _ in range(0, 50):

        index = random.choice(range(len(bet_areas)))

        try:
            wait_If_Clickable(driver, game, bet_areas[index])
        except ElementClickInterceptedException:
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            wait_If_Clickable(driver, game, bet_areas[index])

        insufficient = customJS(driver, 'toast_check("Insufficient Balance");')

        if insufficient:
            screenshot(driver, 'Insufficient Balance', tableDealer[0], allin)
            wait_If_Clickable(driver, 'action', 'confirm')
            waitPresence(driver, 'in-game', 'balance', text='0.00', setTimeout=10)
            message = debuggerMsg(tableDealer, f'All-in bet {coins.text} - Expected: 0.00')
            assertion(message, coins.text, '==', '0.00')
            sumBetPlaced(driver, tableDealer)
            break

# verifies payrates matches with the payrate
# from yaml file
def payrates_odds(driver, game, allin=False):
    defaultPay = []
    list_pays = []
    betLimit = data('bet-limit').get(game)
    tableDealer = table_dealer(driver)

    for _, x in betLimit.items():
        defaultPay.append(x)

    wait_If_Clickable(driver, 'in-game', 'payrate-modal')
    waitElement(driver, 'in-game', 'modal-bet')
    screenshot(driver, 'BET Limit - Payrate', tableDealer[0], allin)
    payrates = findElements(driver, 'in-game', 'payrates')
    sedie_payrates = findElements(driver, 'in-game', 'sedie-payrate')
    
    for payrate in payrates:
        list_pays.append(payrate.text)

    if game == 'baccarat' and s6 == 1:
        defaultPay.append('(1:12)')
        defaultPay[1] = '(1:1)'

    if game == 'sedie':
        for payrate in sedie_payrates:
            list_pays.append(payrate.text)

    if game == 'dragontiger':
        getDT = env('newDT')
        listDT = getDT.split(':')

        if tableDealer[0] in listDT:
            defaultPay[2] = '(1:8)'

    message = debuggerMsg(tableDealer, f'Bet limit rate & Local bet limit rate - Expected: EQUAL')
    assertion(message, defaultPay, '==', list_pays)
    findElement(driver, 'in-game', 'payrate-close', click=True)

# get the total placed chip value
# and compare it to Bets from betting area
def sumBetPlaced(driver, tableDealer, cancel=False, text=None):
    chips = getChipValue(driver)
    total = 0.00

    # check if bet area has 0 chips
    if cancel:
        message = debuggerMsg(tableDealer, f'{text} {chips} - Expected: No chips placed')
        assertion(message, chips, '==', 0)
    else:
        bets = findElement(driver, 'in-game', 'bets')
        if bets != None:
            total = float(bets.text.replace(',',''))
            message = debuggerMsg(tableDealer, f'Placed chips {round(chips, 2)} '\
            f'& Bets {total} - Expected: EQUAL')
            assertion(message, round(chips, 2), '==', total)
        else:
            message = debuggerMsg(tableDealer, f'\033[91m"Bets:" is empty cannot count chips value')
            assertion(message, skip=True)

# new round verification test case
def verifiy_newRound(driver, bet, tableDealer):
    if bet == 'baccarat' or bet == 'three-cards' or bet == 'dragontiger':
        verify_digitalResult(driver, 'bdt', tableDealer)
    elif bet == 'sicbo':
        verify_digitalResult(driver, 'sicbo', tableDealer)
    elif bet == 'roulette':
        verify_digitalResult(driver, 'roulette', tableDealer)
    else:
        waitElementInvis(driver, 'digital results', 'sedie', \
        setTimeout=3, isDigital=True, tableDealer=tableDealer)
    
    sumBetPlaced(driver, tableDealer, cancel=True, text='No placed chips after new round')

def verify_digitalResult(driver, game, tableDealer):
    digital = findElement(driver, 'digital results', game)
    message = debuggerMsg(tableDealer, 'New Round Digital Result is displayed!')
    assertion(message, digital.is_displayed(), '==', False)
 
# verifies in-game roadmap summary visibility and assertion    
def summary(driver, game, tableDealer):
    total = 0
    if game not in ['sicbo', 'roulette']:
        if game == 'baccarat' or 'dragontiger':
            summaries = findElements(driver, 'in-game', 'summary')
            
        if game == 'sedie':
            summaries = findElements(driver, 'in-game', 'sedie-summary')
            sideBtn = findElements(driver, 'in-game', 'sedie-sidebtn')
            for buttons in sideBtn[::-1]:
                buttons.click()
        
        for j, i in enumerate(summaries):
            if game == 'three-cards' and j == 3:
                continue
            if game == 'sedie' and j != 2 and j != 3:
                continue
            
            match = re.search(r'\d+', i.text)
            if match:
                number = int(match.group())
                total += number
        
        shoe = findElement(driver, 'in-game', 'shoe')
        if game in ['three-cards', 'sedie']:
            value = int(shoe.text)
        else:
            value = int(shoe.text.split('-')[1])
            
        message = debuggerMsg(tableDealer, f'Rodmap total summary {total}, '\
        f'Shoe round {value} - Expected: round > total')
        assertion(message, total, '==', value -1)

# check race tracker visibility
def check_raceTracker(driver, tableDealer):
    findElement(driver, 'in-game', 'switch', click=True)
    waitElement(driver, 'in-game', 'race-tracker', setTimeout=3)
    raceTracker = findElement(driver, 'in-game', 'race-tracker')
    message = debuggerMsg(tableDealer, 'Race Tracker is displayed.')
    assertion(message, raceTracker.is_displayed(), '==', True)
    findElement(driver, 'in-game', 'switch', click=True)

# gets table number and dealer name
def table_dealer(driver):
    tableNumber = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game', 'dealer')
    return tableNumber.text, dealer.text

# soft assertion function
def assertion(message, comparison=None, operator=None, comparison2=None, skip=False, notice=False):
    red = '\033[91m'
    green = '\033[32m'
    default = '\033[0m'
    yellow = '\033[93m'
    
    if skip:
        print(f'{yellow}SKIPPED{default} {message}')
        GS_REPORT.append(['SKIPPED'])
    elif notice:
        print(f'{yellow}NOTICE{default} {message}')
    else:
        try:
            if operator == '==':
                assert comparison == comparison2
            elif operator == '>':
                assert comparison > comparison2
            elif operator == '<':
                assert comparison < comparison2
            
            print(f'{green}PASSED{default} {message}')
            GS_REPORT.append(['PASSED'])
        except AssertionError:
            print(f'{red}FAILED{default} {message}')
            GS_REPORT.append(['FAILED'])
            