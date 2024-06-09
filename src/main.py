import uuid
uuid = uuid.uuid1().hex

from . import GS_REPORT, BET_LIMIT
from src.utils.utils import Utilities
from src.components.chat import Chat
from src.api.services import Services
from src.components.chips import Chips
from src.components.bet import Betting
from src.helpers.helpers import Helpers
from src.components.history import History
from src.components.balance import Balance
from src.components.results import Results
from src.components.display import Display

class Main(Helpers):

    def __init__(self) -> None:
        super().__init__()
        self.chat = Chat()
        self.chips = Chips()
        self.bet = Betting()
        self.history = History()
        self.balance = Balance()
        self.results = Results()
        self.display = Display()
        self.utils = Utilities()
        self.services = Services()

    def game_bet(self, driver, gsreport, bet, betArea, allin=False, getBalance=None):
        balance = []
        stream = False
        tableDealer = self.table_dealer(driver)
        self.wait_element(driver, 'in-game', 'timer')
        self.disableStream(driver, stream)
        if allin:
            self.balance.player_balance_assertion(driver, bet, value=getBalance, lobbyBalance=True)
            currHistoryRow = self.history.open_bet_history(driver, bet, tableDealer)
            self.chips.edit_chips(driver, 20, BET_LIMIT=BET_LIMIT)

        while True:
            money = self.search_element(driver, 'in-game', 'balance')
            balance.append(money.text)
            timer = self.search_element(driver, 'in-game', 'timer')
            results = []

            if timer.text == 'CLOSED':
                self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                self.utils.screenshot(driver, 'Please Place Your Bet', tableDealer[0], allin)
            else:
                try:
                    timerInt = int(timer.text.strip())
                except ValueError:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                if timerInt <= 5:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                else:
                    if timerInt >= 10:
                        if allin:
                            self.bet.allin_bet(driver, bet, results, allin)
                        else:
                            self.wait_clickable(driver, bet, betArea)
                            self.wait_element_invisibility(driver, 'in-game', 'toast')
                            self.utils.customJS(driver, f'click(`{self.utils.data("action", "confirm")}`);')

                        self.wait_text_element(driver, 'in-game','toast', text='No More Bets!', timeout=40)
                        remainingMoney = self.search_element(driver, 'in-game', 'balance')
                        preBalance = float(remainingMoney.text.replace(',',''))

                        self.utils.screenshot(driver, 'No More Bets', tableDealer[0], allin)
                        self.wait_element_invisibility(driver, 'in-game', 'toast')
                        self.wait_element(driver, 'in-game', 'toast')
                        
                        if bet not in ['sicbo', 'roulette'] and allin:
                            if self.utils.env('table') in tableDealer[0]:
                                message = self.utils.debuggerMsg(tableDealer, f'Digital Results & {self.utils.env("table")} '\
                                f'Dealer Cards - Expected: Matched')
                                self.utils.assertion(message, all(results))
                            else:
                                message = self.utils.debuggerMsg(tableDealer, 'Card Results in all round are flipped')
                                self.utils.assertion(message, all(results))

                        winner = self.search_element(driver, 'in-game', 'toast')
                        self.utils.screenshot(driver, winner.text, tableDealer[0], allin)

                        # =================================================
                        # get game result text from digital message
                        board = self.search_elements(driver, 'in-game', 'board-result')
                        lucky_odds = dict(self.utils.data('lucky'))
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
                        bets = self.search_element(driver, 'in-game', 'bets')
                        getBets = float(bets.text.replace(',',''))

                        # get balance after bet
                        wl = self.results.win_lose(driver)
                        balance = float(remainingMoney.text.replace(',',''))
                        total = 0

                        # =================================================
                        # calculates the expected lose and win
                        if 'Lose: ' in wl:
                            loseAmount = float(wl.replace('Lose: ',''))
                            calcAmount = max(0, float(preBalance) + float(getBets) - float(loseAmount))

                            if allin:
                                self.utils.screenshot(driver, 'Lose Balance', tableDealer[0], allin)

                            message = self.utils.debuggerMsg(tableDealer, f'Balance after losing {round(calcAmount, 2)} '\
                            f'Latest Balance {round(balance, 2)} - Expected: EQUAL')
                            self.utils.assertion(message, f'{round(calcAmount, 2):.2f}', '==', f'{round(balance, 2):.2f}')

                            if not allin:
                                driver.save_screenshot(f'screenshots/{"Lose Total"} {tableDealer[0]} {uuid[:4]}.png')

                            self.balance.player_balance_assertion(driver, bet)
                        else:
                            resultBal = float(wl.replace('Win: ',''))
                            total = preBalance + resultBal + getBets
                            placeBets = self.search_element(driver, 'in-game', 'bets')
                            cFloat = float(placeBets.text.replace(',',''))

                            # ====================================================
                            # calculate the odds player will receive after winning
                            # special case for Three-cards odds
                            if not allin:
                                import re
                                getOdds = self.search_element(driver, bet, betArea)
                                match = re.search(r'\b(\d+:\d+(\.\d+)?)\b', getOdds.text)
                                if bet != 'sicbo' and bet != 'roulette':
                                    if bet == 'three-cards' and betArea == 'LUCK':
                                        calc_odds = lucky_result * cFloat
                                        message = self.utils.debuggerMsg(tableDealer, f'Odds won: {calc_odds} & '\
                                        f'Balance Result: {resultBal} - Expected: EQUAL')
                                        self.utils.assertion(message, calc_odds, '==', resultBal)
                                    else:
                                        if match:
                                            val = match.group(1)
                                            odds = float(val.split(':', 1)[1])
                                            winOdds = cFloat * odds
                                            if resultBal != 0.00:
                                                message = self.utils.debuggerMsg(tableDealer, f'Odds won: {winOdds} & '\
                                                f'Balance Result: {resultBal} - Expected: EQUAL')
                                                self.utils.assertion(message, winOdds, '==', resultBal)
                                        else:
                                            print("Odds not found")

                            if allin:
                                self.utils.screenshot(driver, 'Win Balance', tableDealer[0], allin)

                            driver.save_screenshot(f'screenshots/{"Win Total"} {tableDealer[0]} {uuid[:4]}.png')
                            # checks if the total winnings + the current balance is
                            # equal to the latest balance
                            message = self.utils.debuggerMsg(tableDealer, f'Win balance {round(total, 2)} & '\
                            f'Latest balance {balance} - Expected: EQUAL')
                            self.utils.assertion(message, f'{round(total, 2)}', '==', f'{round(balance, 2)}')

                        if allin:
                            self.wait_element(driver, 'in-game','toast')
                            self.wait_element_invisibility(driver, 'in-game','toast')
                            self.balance.player_balance_assertion(driver, bet)
                            self.wait_text_element(driver, 'in-game','toast', text='Please Place Your Bet!', timeout=5)
                            self.wait_element_invisibility(driver, 'in-game','toast')
                            self.display.digital_result(driver, bet, tableDealer)

                            if bet == 'roulette':
                                self.display.roulette_race_tracker(driver, tableDealer)

                            # Place a bet when the timer is CLOSED verification
                            self.display.roadmap_summary(driver, bet, tableDealer)
                            self.wait_text_element(driver, 'in-game','toast', text='No More Bets!', timeout=40)
                            if timer.text == 'CLOSED':
                                bet_areas = list(self.utils.data(bet))
                                betRange = 10 if bet in ['sicbo', 'roulette'] else len(bet_areas)
                                ExceptionMessage = []
                                for rangeLength in range(betRange):
                                    try:
                                        self.wait_clickable(driver, bet, bet_areas[rangeLength])
                                    except Exception as e:
                                        ExceptionMessage.append(str(e))

                                self.utils.screenshot(driver, 'Bet on CLOSED', tableDealer[0], allin)
                                message = self.utils.debuggerMsg(tableDealer, f'Failed Clicks {len(ExceptionMessage)} '\
                                f'Bet area length {betRange} - Expected: EQUAL')
                                self.utils.assertion(message, len(ExceptionMessage), '==', betRange)

                            self.bet.payrates_odds(driver, bet, tableDealer, allin) # check if bet limit payrate are equal
                            self.chat.chatbox(driver, bet, tableDealer)
                            self.history.open_bet_history(driver, bet, tableDealer, currHistoryRow, updates=True)
                            if gsreport:
                                self.services.SEND_REPORT(GS_REPORT, bet, tableDealer)
                        break

    def play(self, driver, gsreport, bet, betArea=None, allin=False, name=""):
        print('\n')
        self.wait_element(driver, 'lobby', 'main')
        self.wait_element(driver, 'in-game', 'botnav')
        self.wait_clickable(driver, 'lobby', 'user', 'info')
        self.wait_element(driver, 'lobby', 'user', 'user-modal')
        bet_limit = self.search_element(driver, 'lobby', 'user', 'bet-limit')
        user_limit = int(bet_limit.text.split()[0])
        global BET_LIMIT
        BET_LIMIT = user_limit
        self.wait_clickable(driver, 'lobby', 'user', 'close-modal')
        self.wait_element_invisibility(driver, 'lobby', 'user', 'user-modal')

        if gsreport:
            self.services.CREATE_GSHEET(driver)

        self.wait_clickable(driver, 'category', bet)
        bet_areas = list(self.utils.data(bet))
        elements = self.search_elements(driver, 'lobby', 'table panel')
        for element in range(len(elements)):
            try:
                gameName = elements[element]
                skipping = self.utils.env('tables').split(':')
                skip_tables = any(table in gameName.text for table in skipping)
                
                if bet == 'dragontiger' and name not in gameName.text:
                    continue

                elif bet == 'baccarat' and skip_tables:
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

                elements = self.balance.update_player_balance(driver, bet)
                table = elements[element]
                self.utils.customJS(driver, 'noFullScreen();')
                self.utils.driverJS(driver, 'window.scrollTo(0, 0);')
                self.utils.driverJS(driver, "arguments[0].scrollIntoView();", table)
                getPlayerBalance = self.search_element(driver, 'lobby', 'balance')
                userBalance = getPlayerBalance.text.strip()
                table.click()
                self.wait_element(driver, 'in-game', 'game')

                if betArea == 'All':
                    for area in range(len(bet_areas)):
                        self.game_bet(driver, gsreport, bet, bet_areas[area])
                else:
                    self.game_bet(driver, gsreport, bet, betArea, allin, getBalance=userBalance)

                self.wait_clickable(driver, 'in-game', 'back')
                self.wait_element(driver, 'lobby', 'main')
                elements = self.search_elements(driver, 'lobby', 'table panel')
                print('=' * 100)
            except Exception as e:
                element += 1
                tableDealer = self.table_dealer(driver)
                self.skipOnFail(driver, tableDealer, e)
