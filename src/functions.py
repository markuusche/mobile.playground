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
def checkPlayerBalance(driver):
    dealer = findElement(driver, 'in-game','dealer')
    table = findElement(driver, 'in-game', 'tableNumber')
    coins = findElement(driver, 'in-game', 'balance')
    playerBalance = findElement(driver, 'in-game', 'playerBalance')
    message = f'Table: {table.text} Dealer: {dealer.text} Top Panel Balance: {coins.text}'\
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
    bet_areas = list(data(game))
    coins = findElement(driver, 'in-game','balance')
    table = findElement(driver, 'in-game','tableNumber')

    for _ in range(0, 30):
        index = random.choice(range(len(bet_areas)))
        try:
            wait_If_Clickable(driver, game, bet_areas[index])
        except ElementClickInterceptedException:
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            wait_If_Clickable(driver, game, bet_areas[index])

        insufficient = customJS(driver, 'toast_check();')

        if insufficient:
            screenshot(driver, 'Insufficient Balance', table.text, allin)
            findElement(driver, 'action', 'confirm', click=True)
            waitPresence(driver, 'in-game','balance', text='0.00')
            message = f'Table: {table.text} Coins should be 0.00 after betting all-in: {coins.text}'
            assertion(message, coins.text, '0.00')
            break

# verifies payrates matches with the payrate
# from yaml file
def payrates_odds(driver, game, table, allin=False):
    defaultPay = []
    list_pays = []
    betLimit = data('bet-limit').get(game)
    tableNumber = findElement(driver, 'in-game', 'tableNumber')

    for _, x in betLimit.items():
        defaultPay.append(x)

    wait_If_Clickable(driver, 'in-game', 'payrate-modal')
    waitElement(driver, 'in-game', 'modal-bet')
    screenshot(driver, 'BET Limit - Payrate', table.text, allin)
    payrates = findElements(driver, 'in-game', 'payrates')
    sedie_payrates = findElements(driver, 'in-game', 'sedie-payrate')
    
    for payrate in payrates:
        list_pays.append(payrate.text)

    if game == 'sedie':
        for payrate in sedie_payrates:
            list_pays.append(payrate.text)

    if game == 'dragontiger':
        getDT = env('newDT')
        listDT = getDT.split(':')

        if tableNumber.text in listDT:
            defaultPay[2] = '(1:8)'

    message = f'Table: {table.text} Game Bet Limit Payrate: {list_pays} '\
    f'and Hardcoded Bet Limit Payrate: {defaultPay} should be equal'
    assertion(message, defaultPay, list_pays)
    findElement(driver, 'in-game', 'payrate-close', click=True)

def assertion(name, comparison, comparison2):
    red = '\033[91m'
    green = '\033[32m'
    default = '\033[0m'
    try:
        assert comparison == comparison2
        print(f'{green}✅ PASSED{default} {name}')
    except AssertionError:
        print(f'{red}❌ FAILED{default} {name}')
