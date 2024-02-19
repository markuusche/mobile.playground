from src.modules import *
from src.helpers import *
from src.functions import *

count = 0

# this is where the table looping happens
def play(driver, bet, betArea, allin=False, name=""):
    global count
    print('\n')
    waitElement(driver, 'lobby', 'main')
    waitElement(driver, 'in-game', 'botnav')
    wait_If_Clickable(driver, 'category', bet)
    bet_areas = list(data(bet))
    elements = findElements(driver, 'lobby', 'table panel')

    for i in range(len(elements)):
        gameName = elements[i]
        
        if bet == 'dragontiger' and name not in gameName.text:
            continue

        elif bet == 'baccarat' and i == 0:
            continue
        
        elif bet == 'three-cards' and name not in gameName.text:
            continue
        
        elif bet == 'sedie' and name not in gameName.text:
            continue
            
        elif bet == 'sicbo' and name not in gameName.text:
            continue

        elif bet == 'roulette' and name not in gameName.text:
            continue
        
        if allin:
            elements = reset_coins(driver, bet, 2191.78)
        else:
            elements = reset_coins(driver, bet, 10000)

        table = elements[i]

        customJS(driver, 'noFullScreen();')
        customJS(driver, 'scrollToTop();')
        driver.execute_script("arguments[0].scrollIntoView();", table)
 
        table.click()

        waitElement(driver, 'in-game', 'game')

        if betArea == 'All':
            for x in range(len(bet_areas)):
                betOn(driver, bet, bet_areas[x])
        else:
            betOn(driver, bet, betArea, allin)

        wait_If_Clickable(driver, 'in-game', 'back')
        waitElement(driver, 'lobby', 'main')
        elements = findElements(driver, 'lobby', 'table panel')
        print('=' * 100)

# Main Test Case function for validation and assertions
def betOn(driver, bet, betArea, allin=False):
    '''
    this function:
    assert coins and player balance matched,
    asserts the balance is deducted by betting,
    asserts the remaining balance after betting,
    asserts the the added and lose amount after game results,
    asserts No more bets to be made,
    waits for Successful Bet,
    waits for Betting is open,
    logs the the overall results,
    logs table and dealer name,
    '''
    global count
    balance = []
    tableDealer = table_dealer(driver)
    waitElement(driver, 'in-game', 'timer')
    checkPlayerBalance(driver, bet)

    while True:
        money = findElement(driver, 'in-game', 'balance')
        balance.append(money.text)
        timer = findElement(driver, 'in-game', 'timer')
        
        if timer.text == 'CLOSED':
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            screenshot(driver, 'Please Place Your Bet', tableDealer[0], allin)
        else:
            try:
                timerInt = int(timer.text.strip())
            except ValueError:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

            if timerInt <= 5:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            else:
                if timerInt >= 10:
                    if allin:
                        coins_allin(driver, bet, allin)
                    else:
                        wait_If_Clickable(driver, bet, betArea)
                        waitElementInvis(driver, 'in-game', 'toast')
                        wait_If_Clickable(driver, 'action', 'confirm')

                    waitPresence(driver, 'in-game','toast', text='No More Bets!', setTimeout=40)
                    remainingMoney = findElement(driver, 'in-game', 'balance')
                    preBalance = float(remainingMoney.text.replace(',',''))

                    screenshot(driver, 'No More Bets', tableDealer[0], allin)
                    waitElementInvis(driver, 'in-game', 'toast')
                    waitElement(driver, 'in-game', 'toast')
                    winner = findElement(driver, 'in-game', 'toast')
                    screenshot(driver, winner.text, tableDealer[0], allin)
                                            
                    # =================================================
                    # get game result text from digital message
                    board = findElements(driver, 'in-game', 'board-result')
                    lucky_odds = dict(data('lucky'))
                    lucky_result = 0.00
                    odds = []
                    for i in board:
                        board_result = i.text.split(' – ')[0]

                        if board_result in lucky_odds:
                            value = lucky_odds[board_result]
                            odds.append(value)
                            if len(odds) == 2:
                                if odds[0] > odds[1]:
                                    lucky_result = float(odds[0])
                                else:
                                    lucky_result = float(odds[1])
                            else:
                                lucky_result = float(value)

                    # =================================================
                    bets = findElement(driver, 'in-game', 'bets')
                    getBets = float(bets.text.replace(',',''))

                    # get balance after bet
                    wl = LoseOrWin(driver)
                    balance = float(remainingMoney.text.replace(',',''))
                    total = 0

                    # =================================================
                    # calculates the expected lose and win
                    if 'Lose: ' in wl:
                        loseAmount = float(wl.replace('Lose: ',''))
                        calcAmount = max(0, float(preBalance) + float(getBets) - float(loseAmount))

                        if allin:
                            screenshot(driver, 'Lose Balance', tableDealer[0], allin)
                        
                        message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                        f'Balance after losing {round(calcAmount, 2)} Latest Balance {round(balance, 2)} - Expected: EQUAL'
                        assertion(message, f'{round(calcAmount, 2):.2f}', '==', f'{round(balance, 2):.2f}')
                        
                        if not allin:
                            driver.save_screenshot(f'screenshots/{"Lose Total"} {tableDealer[0]} {count}.png')

                        checkPlayerBalance(driver, bet)
                    else:
                        resultBal = float(wl.replace('Win: ',''))
                        total = preBalance + resultBal + getBets
                        placeBets = findElement(driver, 'in-game', 'bets')
                        cFloat = float(placeBets.text.replace(',',''))

                        # ====================================================
                        # calculate the odds player will receive after winning 
                        getOdds = findElement(driver, bet, betArea)
                        match = re.search(r'\b(\d+:\d+(\.\d+)?)\b', getOdds.text)

                        # special case for Three-cards odds
                        if not allin:
                            if bet != 'sicbo' and bet != 'roulette':
                                if bet == 'three-cards' and betArea == 'Lucky':
                                    count += 1
                                    calc_odds = lucky_result * cFloat
                                    message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                                    f'Odds won: {calc_odds} & Balance Result: {resultBal} - Expected: EQUAL'
                                    assertion(message, calc_odds, '==', resultBal)
                                else:
                                    if match:
                                        val = match.group(1)
                                        odds = float(val.split(':', 1)[1])
                                        winOdds = cFloat * odds
                                        if resultBal != 0.00:
                                            count += 1
                                            message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                                            f'Odds won: {winOdds} & Balance Result: {resultBal} - Expected: EQUAL'
                                            assertion(message, winOdds, '==', resultBal)
                                    else:
                                        print("Odds not found")
                                
                        if allin:
                            screenshot(driver, 'Win Balance', tableDealer[0], allin)
                    
                        driver.save_screenshot(f'screenshots/{"Win Total"} {tableDealer[0]} {count}.png')
                        # checks if the total winnings + the current balance is
                        # equal to the latest balance
                        message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                        f'Win balance {round(total, 2)} & Latest balance {balance} - Expected: EQUAL'
                        assertion(message, f'{round(total, 2)}', '==', f'{round(balance, 2)}')
                        checkPlayerBalance(driver, bet)

                    if allin:
                        waitPresence(driver, 'in-game','toast', text='Please Place Your Bet!', setTimeout=5)
                        waitElementInvis(driver, 'in-game','toast')
                        verifiy_newRound(driver, bet, tableDealer)
                        summary(driver, bet, tableDealer)
                        # Place a bet when the timer is CLOSED verification
                        if bet != 'sicbo' and bet != 'roulette': # ignore sicbo and roulette for now
                            waitPresence(driver, 'in-game','toast', text='No More Bets!', setTimeout=40)
                            if timer.text == 'CLOSED':
                                bet_areas = list(data(bet))
                                ExceptionMessage = []
                                for i in range(len(bet_areas)):
                                    try:
                                        wait_If_Clickable(driver, bet, bet_areas[i])
                                    except Exception as e:
                                        ExceptionMessage.append(str(e))

                                screenshot(driver, 'Bet on CLOSED', tableDealer[0], allin)
                                message = f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
                                f'Failed Clicks {len(ExceptionMessage)} '\
                                f'Bet area length {len(bet_areas)} - Expected: EQUAL'
                                assertion(message, len(ExceptionMessage), '==', len(bet_areas))
                            
                        payrates_odds(driver, bet, allin) # check if bet limit payrate are equal
                        # takes a screenshot of digital message for not betting 3 times                        
                        waitPresence(driver, 'in-game','toast', text='You have NOT bet for 3 times, 2 more and you\'ll be redirected to lobby!')
                        screenshot(driver, 'You have NOT bet for 3 times', tableDealer[0], allin)
                    break
