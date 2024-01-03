from src.modules import *
from src.helper import *
from src.api import *

count = 0

#this is where the table looping and API requests
def play(driver, game, bet, allin=False):
    waitElement(driver, 'in-game', 'botnav')
    wait_If_Clickable(driver, 'category', game)
    elements = findElements(driver, 'lobby', game)
    global count
    for i in range(len(elements)):
        gameName = elements[i]
        if game == 'dragontiger' and 'DT' not in gameName.text:
            continue

        elif game == 'baccarat' and i == 0:
            continue

        elif game == 'three-cards' and 'Three' not in gameName.text:
            continue

        elif game == 'sedie' and 'edie' not in gameName.text:
            continue
            
        if allin:
            elements = reset_coins(driver, game)

        x = elements[i]
        driver.execute_script(executeJS('exitScreen')) 
        driver.execute_script("arguments[0].scrollIntoView();", x)
        sleep(0.5)
        x.click()
        waitElement(driver, 'in-game', 'game')
        playBaccarat(driver, game, bet, allin)

        if game == 'baccarat' and bet == 'All':
            allin = False

        findElement(driver, 'in-game', 'back', click=True)
        sleep(2)
        #closeBanner(driver)
        elements = findElements(driver, 'lobby', game)
        count += 1

#this is where the betting process
def playBaccarat(driver, game, bet, allin=False):
    bet_areas = list(data(game))
    if bet == 'All':
        for i in range(0, len(bet_areas)):
            betOn(driver, game, bet_areas[i])

        betOn(driver, 'action', 'rebet')
    else:
        betOn(driver, game, bet, allin)

def betOn(driver, bet, betArea, allin=False):
    '''
    this function:
    assert coins and player balancec matched,
    asserts the balance is deducted by betting,
    asserts the remaining balance after betting,
    asserts the the added and lose amount after game results,
    asserts No more bets to be made,
    waits for Successful Bet,
    waits for Betting is open,
    logs the the overall results,
    logs table and dealer name,
    '''

    balance = []
    table = findElement(driver, 'in-game','tableNumber')
    dealer = findElement(driver, 'in-game','dealer')

    while True:
        sleep(1)
        money = findElement(driver, 'in-game','balance')
        balance.append(money.text)
        checkPlayerBalance(driver)
        timer = findElement(driver, 'in-game', 'timer')
        
        if timer.text == 'CLOSED':
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            captureDigitalMessage(driver, 'Please Place Your Bet', table.text, allin)
        else:
            intTimer = int(timer.text)
            if intTimer < 5:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                captureDigitalMessage(driver, 'Please Place Your Bet', table.text, allin)
            else:
                if intTimer > 7:
                    if allin:
                        if bet == 'baccarat':
                            coins_allin(driver, bet, allin)

                        elif bet == 'dragontiger':
                            coins_allin(driver, bet, allin)

                        elif bet == 'three-cards':
                            coins_allin(driver, bet, allin)

                        elif bet == 'sedie':
                            coins_allin(driver, bet, allin)

                        else:
                            ...
                    else:
                        wait_If_Clickable(driver, bet, betArea)
                        waitElementInvis(driver, 'in-game', 'toast')
                        findElement(driver, 'action', 'confirm', click=True)

                    waitPresence(driver, 'in-game','toast', text='Bet Successful!')
                    captureDigitalMessage(driver, 'Bet Sucessful', table.text, allin)
                    waitPresence(driver, 'in-game','toast', text='No More Bets!')
                    remainingMoney = findElement(driver, 'in-game', 'balance')
                    preBalance = float(remainingMoney.text.replace(',',''))

                    captureDigitalMessage(driver, 'No More Bets', table.text, allin)
                    waitElementInvis(driver, 'in-game', 'toast')
                    waitElement(driver, 'in-game', 'toast')
                    winner = findElement(driver, 'in-game', 'toast')
                    captureDigitalMessage(driver, winner.text, table.text, allin)

                    bets = findElement(driver, 'in-game', 'bets')
                    getBets = float(bets.text.replace(',',''))
                    oldBalance = float(balance[0].replace(',',''))

                    #balance after bet
                    wl = LoseOrWin(driver)
                    balance = float(remainingMoney.text.replace(',',''))
                    total = 0
                    back = 0
                    if 'Lose: ' in wl:
                        loseAmount = float(wl.replace('Lose: ',''))
                        calcAmount = float(f'{preBalance:.2f}') + float(f'{getBets:.2f}') - float(f'{loseAmount:.2f}')

                        if allin:
                            screenshot(driver, 'Lose Balance', table.text)
                        
                        assert f'{calcAmount:.2f}' == f'{balance:.2f}'
                    else:
                        resultBal = float(wl.replace('Win: ',''))
                        total = float(f'{preBalance:.2f}') + float(f'{resultBal:.2f}') + float(f'{getBets:.2f}')
                        
                        if allin:
                            screenshot(driver, 'Win Balance', table.text)
                    
                        assert f'{total:.2f}' == f'{balance:.2f}'

                    with open('logs.txt', 'a') as logs:
                        logs.write(f'===============================\nIndex: {count}\n{table.text} {dealer.text} - BET on: {betArea}\nCurrent Balance: {oldBalance:.2f}\nBet: {getBets:.2f}\nPre-Balance: {preBalance:.2f}\n{wl}\nCash back: {back}\nFinal Balance: {balance:.2f}\n===============================\n' + '\n')
                    break

# check if the player balance from top left panel icon
# and in the middle panel matches.
def checkPlayerBalance(driver):
    coins = findElement(driver, 'in-game', 'balance')
    playerBalance = findElement(driver, 'in-game', 'playerBalance')
    assert coins.text == playerBalance.text

#gets Lose or Win message with the values
def LoseOrWin(driver):
    waitElement(driver, 'in-game', 'resultToast')
    result = findElement(driver, 'in-game', 'winloss')
    if '-' in result.text:
        getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
        return f'Lose: {getText:.2f}'
    else:
        getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
        return f'Win: {getText:.2f}'

#All-in bet
def coins_allin(driver, game, allin=False):
    bet_areas = list(data(game))
    coins = findElement(driver, 'in-game','balance')
    table = findElement(driver, 'in-game','tableNumber')

    for _ in range(0, 30):
        index = random.choice(range(len(bet_areas)))
        wait_If_Clickable(driver, game, bet_areas[index])
        insufficient = driver.execute_script(executeJS('getDigital'))

        if insufficient == True:
            captureDigitalMessage(driver, 'Insufficient', table.text, allin)
            wait_If_Clickable(driver, 'action', 'confirm')
            sleep(2)
            assert coins.text == '0.00'
            break

#reset coins to default when betting all-in. 
# -this is per table reset-
def reset_coins(driver, game):
    getBalance = addBalance(env('add'))
    addBalance(env('deduc'), amount=getBalance)
    addBalance(env('add'))
    driver.refresh()
    waitElement(driver, 'lobby', 'content')
    #closeBanner(driver)
    sleep(2)
    findElement(driver, 'category', game, click=True)
    elements = findElements(driver, 'lobby', game)
    return elements

def captureDigitalMessage(driver, value, count, allin=False):
    if allin:
        screenshot(driver , value, count)

