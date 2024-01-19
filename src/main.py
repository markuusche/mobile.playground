from src.modules import *
from src.helpers import *
from src.functions import *

count = 0

# this is where the table looping happens
def play(driver, game, bet, allin=False):
    global count

    waitElement(driver, 'lobby', 'main')
    waitElement(driver, 'in-game', 'botnav')
    wait_If_Clickable(driver, 'category', game)
    elements = findElements(driver, 'lobby', game)

    for i in range(len(elements)):
        gameName = elements[i]
        
        # look for 'DT' string on the table list
        if game == 'dragontiger' and 'DT' not in gameName.text:
            continue

        elif game == 'baccarat' and i == 0:
            continue
        
        # look for 'Three' string on the table list
        elif game == 'three-cards' and 'Three' not in gameName.text:
            continue
        
        # look for 'Sedie' string on the table list
        elif game == 'sedie' and 'Sedie' not in gameName.text:
            continue
        
        # use for all-in test case
        if allin:
            elements = reset_coins(driver, game, 1191.78)
        else:
            elements = reset_coins(driver, game, 10000)

        table = elements[i]

        # javascript code to prevent full screen when
        # entering tables
        customJS(driver, 'noFullScreen();')
        customJS(driver, 'scrollToTop();')
        driver.execute_script("arguments[0].scrollIntoView();", table)
 
        # prevent unclickable sedie table (I dont usually use sleep, but here it is)
        sleep(2)

        # click table from the lobby
        table.click()

        # waits for game table to be visible before starting
        waitElement(driver, 'in-game', 'game')

        # playing functions starts here
        playGame(driver, game, bet, allin)

        # going back to lobby after the test is done
        wait_If_Clickable(driver, 'in-game', 'back')
        waitElement(driver, 'lobby', 'main')
        elements = findElements(driver, 'lobby', game)

# this is where the betting process for single bet and Allbet (All)
def playGame(driver, game, bet, allin=False):
    bet_areas = list(data(game))
    if bet == 'All':
        for i in range(len(bet_areas)):
            betOn(driver, game, bet_areas[i])
    else:
        betOn(driver, game, bet, allin)

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
    table = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game','dealer')

    while True:
        count += 1
        money = findElement(driver, 'in-game', 'balance')
        balance.append(money.text)
        waitElement(driver, 'in-game', 'timer')
        checkPlayerBalance(driver)
        timer = findElement(driver, 'in-game', 'timer')
        
        if timer.text == 'CLOSED':
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            screenshot(driver, 'Please Place Your Bet', table.text, allin)
        else:
            try:
                timerInt = int(timer.text.strip())
            except ValueError:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

            if timerInt <= 5:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            else:
                if timerInt >= 7:
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
                        wait_If_Clickable(driver, bet, betArea)
                        waitElementInvis(driver, 'in-game', 'toast')
                        wait_If_Clickable(driver, 'action', 'confirm')

                    waitPresence(driver, 'in-game','toast', text='Bet Successful!')
                    screenshot(driver, 'Bet Sucessful', table.text, allin)
                    waitPresence(driver, 'in-game','toast', text='No More Bets!')
                    remainingMoney = findElement(driver, 'in-game', 'balance')
                    preBalance = float(remainingMoney.text.replace(',',''))

                    screenshot(driver, 'No More Bets', table.text, allin)
                    waitElementInvis(driver, 'in-game', 'toast')
                    waitElement(driver, 'in-game', 'toast')
                    winner = findElement(driver, 'in-game', 'toast')
                    screenshot(driver, winner.text, table.text, allin)
                    
                    # =================================================
                    # get game result text from digital message
                    board = findElements(driver, 'in-game', 'board-result')
                    lucky_odds = dict(data('lucky'))
                    lucky_result = 0.00
                    for i in board:
                        board_result = i.text.split(' – ')[0]

                        if board_result in lucky_odds:
                            value = lucky_odds[board_result]
                            lucky_result = float(value)

                    # =================================================

                    bets = findElement(driver, 'in-game', 'bets')
                    getBets = float(bets.text.replace(',',''))
                    oldBalance = float(balance[0].replace(',',''))

                    # get balance after bet
                    wl = LoseOrWin(driver)
                    balance = float(remainingMoney.text.replace(',',''))
                    total = 0
                    back = 0

                    # =================================================
                    # calculates the expected lose and win
                    if 'Lose: ' in wl:
                        loseAmount = float(wl.replace('Lose: ',''))
                        calcAmount = float(preBalance) + float(getBets) - float(loseAmount)

                        if allin:
                            screenshot(driver, 'Lose Balance', table.text, allin)
                        
                        assert f'{calcAmount:.2f}' == f'{balance:.2f}', f'Table {table.text} calcAmount: {calcAmount} balance: {balance}'\
                        ' \nAmount Calculation and Balance should be equal'

                        checkPlayerBalance(driver)
                    else:
                        resultBal = float(wl.replace('Win: ',''))
                        total = preBalance + resultBal + getBets
                        placeBets = findElement(driver, 'in-game', 'bets')
                        cFloat = float(placeBets.text.replace(',',''))

                    # =================================================

                        # ====================================================
                        # calculate the odds player will receive after winning 
                        getOdds = findElement(driver, bet, betArea)
                        match = re.search(r'\b(\d+:\d+(\.\d+)?)\b', getOdds.text)

                        # special case for Three-cards odds
                        if allin == False:
                            if bet == 'three-cards' and betArea == 'Lucky':
                                calc_odds = lucky_result * cFloat
                                assert calc_odds == resultBal, f'Table {table.text} Calculation Odds: {calc_odds} Result Balance: {resultBal}'\
                                ' \nOdds Calculation and Results Balance should be equal'
                            else:
                                if match:
                                    val = match.group(1)
                                    odds = float(val.split(':', 1)[1])
                                    winOdds = cFloat * odds
                                    if resultBal != 0.00:
                                        assert winOdds == resultBal, f'Table {table.text} winOdds: {winOdds} resultBal: {resultBal}'\
                                        ' \nWinning Odds and Result Balance should be equal'
                                else:
                                    print("Odds not found")
                                
                        if allin:
                            screenshot(driver, 'Win Balance', table.text, allin)
                    
                        driver.save_screenshot(f'screenshots/{"Win Total"} {table.text} {count}.png')
                        # checks if the total winnings + the current balance is
                        # equal to the latest balance
                        assert f'{total:.2f}' == f'{balance:.2f}', f'Table {table.text} Total Amount: {total} Remaining Balance {balance}'\
                        ' \nTotal Amount and Remaning Balance should be equal'

                        checkPlayerBalance(driver)
                    
                    if allin:
                        # Place a bet when the timer is CLOSED verification
                        waitPresence(driver, 'in-game','toast', text='No More Bets!')
                        if timer.text == 'CLOSED':
                            bet_areas = list(data(bet))
                            ExceptionMessage = []
                            for i in range(len(bet_areas)):
                                try:
                                    wait_If_Clickable(driver, bet, bet_areas[i])
                                except Exception as e:
                                    ExceptionMessage.append(str(e))

                            screenshot(driver, 'Bet on CLOSED', table.text, allin)
                            assert len(ExceptionMessage) == len(bet_areas), f'Table {table.text} Expected Failed Clicks: {len(ExceptionMessage)} Bet Area Length {len(bet_areas)}'\
                            ' \nFailed clicks count should be equal to Bet Area Length Count'

                        # check if bet limit payrate are equal
                        payrates_odds(driver, bet, table, allin)

                         # takes a screenshot of digital message for not betting 3 times
                        waitPresence(driver, 'in-game','toast', text='You have NOT bet for 3 times, 2 more and you\'ll be redirected to lobby!')
                        screenshot(driver, 'You have NOT bet for 3 times', table.text, allin)

                    with open('logs.txt', 'a') as logs:
                        logs.write(f'===============================\n{table.text} {dealer.text} - BET on: {betArea}\nCurrent Balance: {oldBalance:.2f}\nBet: {getBets:.2f}\nPre-Balance: {preBalance:.2f}\n{wl}\nCash back: {back}\nFinal Balance: {balance:.2f}\nWin Result: {total} - {balance}\n===============================\n' + '\n')
                    break
