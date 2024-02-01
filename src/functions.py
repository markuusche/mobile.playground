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
        message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] Top Panel Balance: {coins.text}'\
        f' and Bottom Panel Balance: {playerBalance.text} should be equal'
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

# Bet all coins until Insufficient funds message appear
def coins_allin(driver, game, allin=False):
    global s6

    coins = findElement(driver, 'in-game','balance')
    tableDealer = table_dealer(driver)
    bet_areas = list(data(game))
    s6 = random.choice(range(0, 2))

    if s6 == 1 and game == 'baccarat':
        wait_If_Clickable(driver, 'super6', 'r-area')
        waitElement(driver, 'super6', 's6')
        wait_If_Clickable(driver, 'super6', 's6')

    for _ in range(0, 30):

        index = random.choice(range(len(bet_areas)))

        try:
            wait_If_Clickable(driver, game, bet_areas[index])
        except ElementClickInterceptedException:
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            wait_If_Clickable(driver, game, bet_areas[index])

        insufficient = customJS(driver, 'toast_check("Insufficient Balance");')

        if insufficient:
            screenshot(driver, 'Insufficient Balance', tableDealer[0], allin)
            findElement(driver, 'action', 'confirm', click=True)
            waitPresence(driver, 'in-game','balance', text='0.00')
            message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
            f'Coins: {coins.text} should be 0.00 after betting all-in'
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
    f'Game Bet Limit Payrate: {list_pays} '\
    f'and Hardcoded Bet Limit Payrate: {defaultPay} should be equal'
    assertion(message, defaultPay, list_pays)
    findElement(driver, 'in-game', 'payrate-close', click=True)

# get the total placed chip value
# and compare it to Bets from betting area
def sumBetPlaced(driver, table, dealer):
    chips = 0.00
    placed_chips = findElements(driver, 'in-game', 'totalMoney')
    bets = findElement(driver, 'in-game', 'bets')
    total = float(bets.text.replace(',',''))

    for i in placed_chips:
        if i.text != '':
            chips += float(i.text.replace(',',''))

    message = f'[Table: {table} Dealer: {dealer}] '\
    f'Total Placed Bets Value: {chips} '\
    f'and Bets: {total} should be equal'
    assertion(message, chips, total)

# gets table number and dealer name
def table_dealer(driver):
    tableNumber = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game','dealer')
    return tableNumber.text, dealer.text

# wannabe soft assertion function lol
def assertion(name, comparison, comparison2):
    red = '\033[91m'
    green = '\033[32m'
    default = '\033[0m'
    try:
        assert comparison == comparison2
        print(f'{green}PASSED{default} {name}')
    except AssertionError:
        print(f'{red}FAILED{default} {name}')
