from src.modules import *
from src.helper import *
from src.api import *

count = 0

#this is where the table looping and API requests
def play(driver, game, bet, allin=False):
    findElement(driver, 'category', game, click=True)
    elements = findElements(driver, 'lobby', game)
    global count
    for i in range(len(elements)):
        gameName = elements[i]
        if game == 'dragontiger':
            if 'DT' in gameName.text:
                pass
            else:
                continue

            if allin:
                elements = reset_coins(driver, game)

        elif game == 'baccarat':
            if i == len(elements) - 1:
                break

            if allin:
                elements = reset_coins(driver, game)
        
        elif game == 'three-cards':
            if 'Three' in gameName.text:
                pass
            else:
                continue
            
            if allin:
                elements = reset_coins(driver, game)

        x = elements[i]
        driver.execute_script(exitFullScreen()) 
        driver.execute_script("arguments[0].scrollIntoView();", x)
        x.click()
        waitElement(driver, 'in-game', 'game')
        playBaccarat(driver, game, bet, allin)

        if bet == 'All':
            allin = False

        findElement(driver, 'in-game', 'back', click=True)
        closeBanner(driver)
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
        else:
            intTimer = int(timer.text)
            if intTimer <= 7:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            else:
                if intTimer >= 8:
                    if allin:
                        if bet == 'baccarat':
                            coins_allin(driver, bet)

                        elif bet == 'dragontiger':
                            coins_allin(driver, bet)
                        elif bet == 'three-cards':
                            coins_allin(driver, bet)

                        else:
                            ...
                    else:
                        wait_If_Clickable(driver, bet, betArea)
                        findElement(driver, 'action', 'confirm', click=True)

                    waitPresence(driver, 'in-game','toast', text='Bet Successful!')
                    waitPresence(driver, 'in-game','toast', text='No More Bets!')
                    waitElementInvis(driver, 'in-game', 'toast')
                    screenshot(driver, 'capture', count)
                    bets = findElement(driver, 'in-game', 'bets')
                    getBets = float(bets.text.replace(',',''))
                    oldBalance = float(balance[0].replace(',',''))
                    remainingMoney = findElement(driver, 'in-game', 'balance')

                    #balance after bet
                    preBalance = float(remainingMoney.text.replace(',',''))
                    wl = LoseOrWin(driver)
                    balance = float(remainingMoney.text.replace(',',''))
                    total = 0
                    back = 0
                    if 'Lose: ' in wl:
                        loseAmount = float(wl.replace('Lose: ',''))
                        calcAmount = loseAmount - getBets
                        q = abs(calcAmount)
                        back = f'{q:.2f}'
                        resultBalance = q + preBalance
                        screenshot(driver, 'Lose Balance', count)
                        assert f'{resultBalance:.2f}' == f'{balance:.2f}'
                    else:
                        resultBal = float(wl.replace('Win: ',''))
                        total = (preBalance + resultBal) + getBets
                        screenshot(driver, 'Win Balance', count)
                        assert f'{total:.2f}' == f'{balance:.2f}'
                    
                    print(f'===============================\nIndex: {count}\n{table.text} {dealer.text} - BET on: {betArea}\nCurrent Balance: {oldBalance:.2f}\nBet: {getBets:.2f}\nPre-Balance: {preBalance:.2f}\n{wl}\nCash back: {back}\nFinal Balance: {balance:.2f}\n===============================\n')
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
def coins_allin(driver, game):
    bet_areas = list(data(game))
    bet1 = list(data(game))
    coins = findElement(driver, 'in-game','balance')
    if game == 'baccarat':
        for i in bet1:
            bet_areas.append(i)
            bet_areas.append(i)
            
    if game == 'dragontiger' or game == 'three-cards':
        for i in bet1:
            bet_areas.append(i)
            bet_areas.append(i)
            bet_areas.append(i)
    
    for _ in range(len(bet_areas)):
        index = random.choice(range(len(bet_areas)))
        insufficient = findElement(driver , 'in-game', 'insufficient')
        wait_If_Clickable(driver, game, bet_areas[index])
        if insufficient.text == 'Insufficient Balance':
            findElement(driver, 'action', 'confirm', click=True)
            sleep(1)
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
    closeBanner(driver)
    findElement(driver, 'category', game, click=True)
    elements = findElements(driver, 'lobby', game)
    return elements