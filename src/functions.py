from src.modules import *
from src.helpers import *
from src.api import *

# for digital message screenshots
def screenshot(driver, name, val, allin=False):
    if allin:
        driver.save_screenshot(f'screenshots/{name} {val}.png')

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
    getBalance = addBalance(env('add'), amount)
    addBalance(env('deduc'), amount=getBalance)
    addBalance(env('add'), amount)
    driver.refresh()
    waitElement(driver, 'lobby', 'main')
    wait_If_Clickable(driver, 'category', game)
    elements = findElements(driver, 'lobby', game)
    return elements

# check if the player balance from top left panel icon
# and in the middle panel matches.
def checkPlayerBalance(driver, game):
    if game != 'roulette':
        tableDealer = table_dealer(driver)
        coins = findElement(driver, 'in-game', 'balance')
        playerBalance = findElement(driver, 'in-game', 'playerBalance')
        message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] Top balance {coins.text} '\
        f'Bottom balance {playerBalance.text} - Expected: EQUAL'
        assertion(message, coins.text, playerBalance.text)

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
    sumBetPlaced(driver, tableDealer[0], tableDealer[1], cancel=True, text=texts)

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
    numbers = editChips(driver)
    betting(driver, betArea, game)
    chips = getChipValue(driver)
    assert chips > numbers

    cancelAssert(driver, tableDealer, allin, 'Chip placed & cancelled!')
    betting(driver, betArea, game, placeConfirm=True)
    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
    wait_If_Clickable(driver, 'action', 'rebet')

    insufficient = customJS(driver, 'toast_check("Insufficient funds to rebet!");')
    message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
    f'Insufficient funds to rebet! Unable to Rebet and Cancel'
    if insufficient:
        assertion(message, skip=True)
    else:
        cancelAssert(driver, tableDealer, allin, 'Rebet & Cancelled!')
        wait_If_Clickable(driver, 'action', 'rebet')
        wait_If_Clickable(driver, 'action', 'confirm')
        screenshot(driver, 'Rebet & Confirmed!', tableDealer[0], allin)
        waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

# edit chips from in-game
def editChips(driver):
    bets = findElement(driver, 'in-game', 'balance')
    value = float(bets.text.replace(',',''))
    chips = int(value) / 9
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

    # cancelRebet(driver, bet_areas, tableDealer, game, allin=True)
    editChips(driver)

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

        # to remember -> raise a bug regarding inconsistent balance and bet value
        # from betting all-in
        if insufficient:
            screenshot(driver, 'Insufficient Balance', tableDealer[0], allin)
            wait_If_Clickable(driver, 'action', 'confirm')
            waitPresence(driver, 'in-game', 'balance', text='0.00')
            message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'All-in bet {coins.text} - Expected: 0.00'
            assertion(message, coins.text, '0.00')
            break

    sumBetPlaced(driver, tableDealer[0], tableDealer[1])

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

    message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
    f'Bet limit rate & Local bet limit rate - Expected: EQUAL'
    assertion(message, defaultPay, list_pays)
    findElement(driver, 'in-game', 'payrate-close', click=True)

# get the total placed chip value
# and compare it to Bets from betting area
def sumBetPlaced(driver, table, dealer, cancel=False, text=None):
    chips = getChipValue(driver)
            
    # check if bet area has 0 chips
    if cancel:
        message = f'[Table: {table} Dealer: {dealer}] '\
        f'{text} {chips} - Expected: No chips placed'
        assertion(message, chips, 0)
    else:
        bets = findElement(driver, 'in-game', 'bets')
        total = float(bets.text.replace(',',''))

        message = f'[Table: {table} Dealer: {dealer}] '\
        f'Placed chips {round(chips, 2)} '\
        f'Bets {total} - Expected: EQUAL'
        assertion(message, round(chips, 2), total)

# gets table number and dealer name
def table_dealer(driver):
    tableNumber = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game', 'dealer')
    return tableNumber.text, dealer.text

# wannabe soft assertion function lol
def assertion(message, comparison=None, comparison2=None, skip=False):
    red = '\033[91m'
    green = '\033[32m'
    default = '\033[0m'
    yellow = '\033[93m'
    if skip:
        print(f'{yellow}SKIPPED{default} {message}')
    else:
        try:
            assert comparison == comparison2
            print(f'{green}PASSED{default} {message}')
        except AssertionError:
            print(f'{red}FAILED{default} {message}')
