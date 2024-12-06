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

    def game_bet(self, driver, gsreport, bet, getBalance=None):
        balance = []
        stream = False
        tableDealer = self.table_dealer(driver)
        self.wait_element(driver, 'in-game', 'timer')
        self.disableStream(driver, stream)
        self.balance.player_balance_assertion(driver, bet, value=getBalance, lobbyBalance=True)
        currHistoryRow = self.history.open_bet_history(driver, bet, tableDealer)
        self.chips.edit_chips(driver, 20)

        while True:
            money = self.search_element(driver, 'in-game', 'balance')
            balance.append(money.text)
            timer = self.search_element(driver, 'in-game', 'timer')
            results = []

            if timer.text == 'CLOSED':
                self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                self.utils.screenshot(driver, 'Please Place Your Bet', tableDealer[0])
            else:
                try:
                    timerInt = int(timer.text.strip())
                except ValueError:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                if timerInt <= 5:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                else:
                    if timerInt >= 10:
                        self.bet.allin_bet(driver, bet, results)
                        self.wait_text_element(driver, 'in-game','toast', text='No More Bets!', timeout=40)
                        self.utils.screenshot(driver, 'No More Bets', tableDealer[0])
                        self.wait_element_invisibility(driver, 'in-game', 'toast')
                        self.wait_element(driver, 'in-game', 'toast')
                        self.results.game_results(driver, bet, tableDealer)
                        
                        if bet not in ['sicbo', 'roulette', 'sedie']:
                            if self.utils.env('table') in tableDealer[0]:
                                message = self.utils.debuggerMsg(tableDealer, f'Digital Results & {self.utils.env("table")} '\
                                f'Dealer Cards Matched')
                                self.utils.assertion(message, all(results))
                            else:
                                message = self.utils.debuggerMsg(tableDealer, 'Card Results in all round are flipped')
                                self.utils.assertion(message, all(results))
                        
                        self.balance.player_balance_assertion(driver, bet)
                        self.display.digital_result(driver, bet, tableDealer)
   
                        if bet == 'roulette':
                            self.display.roulette_race_tracker(driver, tableDealer)

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

                            self.utils.screenshot(driver, 'Bet on CLOSED', tableDealer[0])
                            message = self.utils.debuggerMsg(tableDealer, f'Failed Clicks {len(ExceptionMessage)} '\
                            f'Bet area length {betRange}')
                            self.utils.assertion(message, len(ExceptionMessage), '==', betRange)

                        self.bet.payrates_odds(driver, bet, tableDealer)
                        self.chat.chatbox(driver, bet, tableDealer)
                        self.history.open_bet_history(driver, bet, tableDealer, currHistoryRow, updates=True)
                        if gsreport:
                            global GS_REPORT
                            self.services.SEND_REPORT(GS_REPORT, bet, tableDealer)
                        break

    def skipper(self, gameName, numbers, name):
        skip = False
        for number in numbers:
            if number in gameName:
                skip = True
                break
        
        # specific table number or table name
        if name not in gameName:
            return True
        
        return skip

    def play(self, driver, gsreport, bet, name=""):
        print('\n')
        self.wait_element(driver, 'lobby', 'main')
        self.wait_element(driver, 'in-game', 'botnav')
        self.wait_clickable(driver, 'lobby', 'user', 'info')
        self.wait_element(driver, 'lobby', 'user', 'user-modal')
        bet_limit = self.search_element(driver, 'lobby', 'user', 'bet-limit')
        user_limit = int(bet_limit.text.split()[0])
        global BET_LIMIT
        BET_LIMIT.append(user_limit)
        self.wait_clickable(driver, 'lobby', 'user', 'close-modal')
        self.wait_element_invisibility(driver, 'lobby', 'user', 'user-modal')

        if gsreport:
            self.services.CREATE_GSHEET(driver)

        self.wait_clickable(driver, 'category', bet)
        elements = self.search_elements(driver, 'lobby', 'table panel')
        
        for element in range(len(elements)):
            try:
                gameName = elements[element]
                tables = self.utils.env('tables', True)
                games = self.utils.env('games', True)
                
                if bet in games:
                    skip = self.skipper(f'{gameName.text.strip()}', tables, name)
                    if skip:
                        continue
                
                elements = self.balance.update_player_balance(driver, bet)
                self.utils.screenshot(driver, 'Lobby', 'Balance')
                table = elements[element]
                self.utils.customJS(driver, 'noFullScreen();')
                self.utils.driverJS(driver, 'window.scrollTo(0, 0);')
                self.utils.driverJS(driver, "arguments[0].scrollIntoView({block: 'center'});", table)
                getPlayerBalance = self.search_element(driver, 'lobby', 'balance')
                userBalance = getPlayerBalance.text.strip()
                table.click()
                self.wait_element(driver, 'in-game', 'game')
                self.game_bet(driver, gsreport, bet, getBalance=userBalance)
                self.wait_clickable(driver, 'in-game', 'back')
                self.wait_element(driver, 'lobby', 'main')
                elements = self.search_elements(driver, 'lobby', 'table panel')
                print('=' * 100)
            except Exception as e:
                self.skipOnFail(driver, e)
                elements = self.search_elements(driver, 'lobby', 'table panel')
