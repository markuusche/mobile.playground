from src.modules import *
from src.helper import *
from src.api import *

#this is where the table looping and API requests
def play(driver, game, bet, allin=False):
    findElement(driver, 'category', game, click=True)
    elements = findElements(driver, 'lobby', 'panel')
    for i in range(1, len(elements)):
        if i == len(elements) - 1:
            break

        if allin:
            getBalance = addBalance(env('add'))
            addBalance(env('deduc'), amount=getBalance)
            addBalance(env('add'))
            driver.refresh()
            waitElement(driver, 'lobby', 'content')
            closeBanner(driver)
            findElement(driver, 'category', game, click=True)
            elements = findElements(driver, 'lobby', 'panel')

        x = elements[i]
        driver.execute_script(exitFullScreen())
        driver.execute_script("arguments[0].scrollIntoView();", x)
        x.click()
        waitElement(driver, 'in-game', 'game')
        
        if bet == 'All':
            allin = False
        
        playBaccarat(driver, game, bet, allin)

        findElement(driver, 'in-game', 'back', click=True)
        closeBanner(driver)
        elements = findElements(driver, 'lobby', 'panel')

#this is where the betting process
def playBaccarat(driver, game, bet, allin=False):
    if game == 'baccarat':
        bet_areas = list(data('baccarat'))
        if bet == 'All':
            for i in range(0, len(bet_areas)):
                betOn(driver, 'baccarat', bet_areas[i])
            
            betOn(driver, 'action', 'rebet')
        else:
            betOn(driver, 'baccarat', bet, allin)

    elif game == 'dragontiger':
        ...

def betOn(driver, bet, betArea, allin=False):
    '''
    this function:
    assert coins and player balancec matched
    asserts the balance is deducted by betting
    asserts the remaining balance after betting
    asserts the the added and lose amount after game results
    asserts No more bets to be made
    waits for Successful Bet
    waits for Betting is open
    logs the the overall results
    logs table and dealer name
    '''

    balance = []
    table = findElement(driver, 'in-game','tableNumber')
    dealer = findElement(driver, 'in-game','dealer')
    while True:
        sleep(1)
        money = findElement(driver, 'in-game','balance')
        balance.append(money.text)
        checkPlayerBalance(driver)
        waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

        if allin:
            bet_areas = list(data('baccarat'))
            for _ in range(10):
                insufficient = findElement(driver , 'in-game', 'insufficient')
                for i in range(len(bet_areas)):
                    wait_If_Clickable(driver, 'baccarat', bet_areas[i])
                    insufficient = findElement(driver , 'in-game', 'insufficient')
                    if insufficient.text == 'Insufficient Balance':
                        findElement(driver, 'action', 'confirm', click=True)
                        findElement(driver, 'action', 'confirm', click=True)
                        sleep(2)
                        money = findElement(driver, 'in-game','balance')
                        assert money.text == '0.00'
                        break
                else:
                    continue
                break
        else:
            wait_If_Clickable(driver, bet, betArea)
            findElement(driver, 'action', 'confirm', click=True)
            findElement(driver, 'action', 'confirm', click=True)

        waitPresence(driver, 'in-game','toast', text='Bet Successful!')
        waitPresence(driver, 'in-game','toast', text='No More Bets!')

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
            assert f'{resultBalance:.2f}' == f'{balance:.2f}'
        else:
            resultBal = float(wl.replace('Win: ',''))
            total = (preBalance + resultBal) + getBets
            assert total == balance

        print(f'===============================\n{table.text} {dealer.text} - BET on: {betArea}\nCurrent Balance: {oldBalance:.2f}\nBet: {getBets:.2f}\nPre-Balance: {preBalance:.2f}\n{wl}\nCash back: {back}\nFinal Balance: {balance:.2f}\n===============================\n')
        break

def checkPlayerBalance(driver):
    # check if the player balance from top left panel icon
    # and in the middle panel matches.
    coins = findElement(driver, 'in-game', 'balance')
    playerBalance = findElement(driver, 'in-game', 'playerBalance')
    assert coins.text == playerBalance.text

def LoseOrWin(driver):
    waitElement(driver, 'in-game', 'resultToast')
    result = findElement(driver, 'in-game', 'winloss')
    if '-' in result.text:
        getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
        return f'Lose: {getText:.2f}'
    else:
        getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
        return f'Win: {getText:.2f}'

