import src.utilities.functions as clss
from . import GS_REPORT

class Main(
    clss.BetAllin,
    clss.Results,
    clss.History,
    clss.PlayerUpdate,
    clss.Chat,
    clss.BetPool
    ):
    
    count = 0
    # Main Test Case function for validation and assertions
    def betOn(self, driver, gsreport, bet, betArea, allin=False, getBalance=None):
        global count
        balance = []
        stream = False
        tableDealer = self.table_dealer(driver)
        self.waitElement(driver, 'in-game', 'timer')
        self.disableStream(driver, stream)
        if allin:
            self.checkPlayerBalance(driver, bet, value=getBalance, lobbyBalance=True)
            currHistoryRow = self.openBetHistory(driver, bet, tableDealer)
            self.editChips(driver, 20)

        while True:
            money = self.findElement(driver, 'in-game', 'balance')
            balance.append(money.text)  
            timer = self.findElement(driver, 'in-game', 'timer')
            results = []

            if timer.text == 'CLOSED':
                self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                self.screenshot(driver, 'Please Place Your Bet', tableDealer[0], allin)
            else:
                try:
                    timerInt = int(timer.text.strip())
                except ValueError:
                    self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                if timerInt <= 5:
                    self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                else:
                    if timerInt >= 10:
                        if allin:
                            self.gameplay(driver, bet, results, allin)
                        else:
                            self.wait_If_Clickable(driver, bet, betArea)
                            self.waitElementInvis(driver, 'in-game', 'toast')
                            self.wait_If_Clickable(driver, 'action', 'confirm')

                        self.waitPresence(driver, 'in-game','toast', text='No More Bets!', setTimeout=40)
                        remainingMoney = self.findElement(driver, 'in-game', 'balance')
                        preBalance = float(remainingMoney.text.replace(',',''))

                        self.screenshot(driver, 'No More Bets', tableDealer[0], allin)
                        self.waitElementInvis(driver, 'in-game', 'toast')
                        self.waitElement(driver, 'in-game', 'toast')
                        
                        if self.env('table') in tableDealer[0]:
                            message = self.debuggerMsg(tableDealer, f'Digital Results & {self.env('table')} Dealer Cards Matched in all round - Expected: EQUAL')
                            self.assertion(message, all(results))
                        else:
                            message = self.debuggerMsg(tableDealer, 'Card Results in all round are flipped')
                            self.assertion(message, all(results))
                            
                        winner = self.findElement(driver, 'in-game', 'toast')
                        self.screenshot(driver, winner.text, tableDealer[0], allin)
                                                
                        # =================================================
                        # get game result text from digital message
                        board = self.findElements(driver, 'in-game', 'board-result')
                        lucky_odds = dict(self.data('lucky'))
                        lucky_result = 0.00
                        odds = []
                        for results in board:
                            board_result = results.text.split(' – ')[0]

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
                        bets = self.findElement(driver, 'in-game', 'bets')
                        getBets = float(bets.text.replace(',',''))

                        # get balance after bet
                        wl = self.LoseOrWin(driver)
                        balance = float(remainingMoney.text.replace(',',''))
                        total = 0

                        # =================================================
                        # calculates the expected lose and win
                        if 'Lose: ' in wl:
                            loseAmount = float(wl.replace('Lose: ',''))
                            calcAmount = max(0, float(preBalance) + float(getBets) - float(loseAmount))

                            if allin:
                                self.screenshot(driver, 'Lose Balance', tableDealer[0], allin)
                            
                            message = self.debuggerMsg(tableDealer, f'Balance after losing {round(calcAmount, 2)} '\
                            f'Latest Balance {round(balance, 2)} - Expected: EQUAL')
                            self.assertion(message, f'{round(calcAmount, 2):.2f}', '==', f'{round(balance, 2):.2f}')
                            
                            if not allin:
                                driver.save_screenshot(f'screenshots/{"Lose Total"} {tableDealer[0]} {count}.png')

                            self.checkPlayerBalance(driver, bet)
                        else:
                            resultBal = float(wl.replace('Win: ',''))
                            total = preBalance + resultBal + getBets
                            placeBets = self.findElement(driver, 'in-game', 'bets')
                            cFloat = float(placeBets.text.replace(',',''))

                            # ====================================================
                            # calculate the odds player will receive after winning 
                            # special case for Three-cards odds
                            if not allin:
                                import re
                                getOdds = self.findElement(driver, bet, betArea)
                                match = re.search(r'\b(\d+:\d+(\.\d+)?)\b', getOdds.text)
                                if bet != 'sicbo' and bet != 'roulette':
                                    if bet == 'three-cards' and betArea == 'LUCK':
                                        count += 1
                                        calc_odds = lucky_result * cFloat
                                        message = self.debuggerMsg(tableDealer, f'Odds won: {calc_odds} & '\
                                        f'Balance Result: {resultBal} - Expected: EQUAL')
                                        self.assertion(message, calc_odds, '==', resultBal)
                                    else:
                                        if match:
                                            val = match.group(1)
                                            odds = float(val.split(':', 1)[1])
                                            winOdds = cFloat * odds
                                            if resultBal != 0.00:
                                                count += 1
                                                message = self.debuggerMsg(tableDealer, f'Odds won: {winOdds} & '\
                                                f'Balance Result: {resultBal} - Expected: EQUAL')
                                                self.assertion(message, winOdds, '==', resultBal)
                                        else:
                                            print("Odds not found")
                                    
                            if allin:
                                self.screenshot(driver, 'Win Balance', tableDealer[0], allin)
                        
                            driver.save_screenshot(f'screenshots/{"Win Total"} {tableDealer[0]} {count}.png')
                            # checks if the total winnings + the current balance is
                            # equal to the latest balance
                            message = self.debuggerMsg(tableDealer, f'Win balance {round(total, 2)} & '\
                            f'Latest balance {balance} - Expected: EQUAL')
                            self.assertion(message, f'{round(total, 2)}', '==', f'{round(balance, 2)}')
                            self.checkPlayerBalance(driver, bet)

                        if allin:
                            self.waitPresence(driver, 'in-game','toast', text='Please Place Your Bet!', setTimeout=5)
                            self.waitElementInvis(driver, 'in-game','toast')
                            self.verifiy_newRound(driver, bet, tableDealer)
                            
                            if bet == 'roulette':
                                self.check_raceTracker(driver, tableDealer)
                                
                            # Place a bet when the timer is CLOSED verification
                            self.summary(driver, bet, tableDealer)
                            self.waitPresence(driver, 'in-game','toast', text='No More Bets!', setTimeout=40)
                            if timer.text == 'CLOSED':
                                bet_areas = list(self.data(bet))
                                betRange = 10 if bet in ['sicbo', 'roulette'] else len(bet_areas)
                                ExceptionMessage = []
                                for rangeLength in range(betRange):
                                    try:
                                        self.wait_If_Clickable(driver, bet, bet_areas[rangeLength])
                                    except Exception as e:
                                        ExceptionMessage.append(str(e))

                                self.screenshot(driver, 'Bet on CLOSED', tableDealer[0], allin)
                                message = self.debuggerMsg(tableDealer, f'Failed Clicks {len(ExceptionMessage)} '\
                                f'Bet area length {betRange} - Expected: EQUAL')
                                self.assertion(message, len(ExceptionMessage), '==', betRange)
                                
                            self.payrates_odds(driver, bet, tableDealer, allin) # check if bet limit payrate are equal
                            self.chat(driver, bet, tableDealer)
                            self.openBetHistory(driver, bet, tableDealer, currHistoryRow, updates=True)
                            if gsreport:
                                self.sendReport(GS_REPORT, bet, tableDealer)
                        break

    def play(self, driver, gsreport, bet, betArea=None, allin=False, name=""):
        global count
        print('\n')
        self.waitElement(driver, 'lobby', 'main')
        self.waitElement(driver, 'in-game', 'botnav')

        if gsreport:
            self.createNew_sheet(driver)

        self.wait_If_Clickable(driver, 'category', bet)
        bet_areas = list(self.data(bet))
        elements = self.findElements(driver, 'lobby', 'table panel')
        for element in range(len(elements)):
            try:
                gameName = elements[element]
                if bet == 'dragontiger' and name not in gameName.text:
                    continue

                elif bet == 'baccarat' and element <= 3:
                    continue
                
                elif bet == 'three-cards' and name not in gameName.text:
                    continue
                
                elif bet == 'sedie' and name not in gameName.text:
                    continue
                    
                elif bet == 'sicbo' and name not in gameName.text:
                    continue

                elif bet == 'roulette' and name not in gameName.text:
                    continue

                elif bet == 'bull bull' and name not in gameName.text:
                    continue
                
                elements = self.updateBalance(driver, bet)
                table = elements[element]
                self.customJS(driver, 'noFullScreen();')
                self.driverJS(driver, 'window.scrollTo(0, 0);')
                self.driverJS(driver, "arguments[0].scrollIntoView();", table)
                getPlayerBalance = self.findElement(driver, 'lobby', 'balance')
                userBalance = getPlayerBalance.text.strip()
                table.click()
                self.waitElement(driver, 'in-game', 'game')

                if betArea == 'All':
                    for area in range(len(bet_areas)):
                        self.betOn(driver, gsreport, bet, bet_areas[area])
                else:
                    self.betOn(driver, gsreport, bet, betArea, allin, getBalance=userBalance)

                self.wait_If_Clickable(driver, 'in-game', 'back')
                self.waitElement(driver, 'lobby', 'main')
                elements = self.findElements(driver, 'lobby', 'table panel')
                print('=' * 100)
            except Exception as e:
                element += 1
                tableDealer = self.table_dealer(driver)
                self.skipOnFail(driver, tableDealer, e)