from decimal import Decimal
from collections import Counter
from src.helpers.helpers import Helpers
from src.components.chips import Chips
from src.utils.utils import Utilities
from src.utils.decoder import Decoder
from selenium.webdriver.common.by import By

class Results(Helpers):
    
    def __init__(self) -> None:
        super().__init__()
        self.chips = Chips()
        self.decoder = Decoder()
        self.utils = Utilities()
        
    def game_results(self, driver, bet, tableDealer):
        """
        Calculates the results of a betting round and compares the player's balance based on winnings and losses.

        This function handles the outcome of two games: 'baccarat' and 'dragontiger'. 
        It retrieves the winner, calculates winnings and losses based on the bet placed, 
        and updates the player's balance accordingly.

        Parameters:
            driver: WebDriver instance used to interact with the web page.
            bet (str): The type of bet ('baccarat' or 'dragontiger').
            tableDealer (list): A list containing dealer information to be used in logging or debugging.

        """

        if bet in ['baccarat', 'dragontiger']:
            balance = self.chips.get_chip_value(driver)
            winnings = 0.0
            loss = 0.0
            
            win_results = self.search_elements(driver, 'in-game', 'win results')
            lose_results = self.search_elements(driver, 'in-game', 'loss results')
            odds = dict(self.utils.data('odds', bet))
            
            def calculate_winnings(chips, betnames):
                total_winnings = 0.00
                playerResult = self.search_element(driver, 'results', 'player points')
                bankerResult = self.search_element(driver, 'results', 'banker points')
                playerPoints = int(playerResult.text) if playerResult.text != '' else 0
                bankerPoints = int(bankerResult.text) if bankerResult.text != '' else 0

                for chip, bet_area in zip(chips, betnames):
                    if chip.text != '':
                        winning_odds = odds[bet_area.text.strip()]
                        chipValue = float(chip.text.replace(',','')) if chip.text != '' else 0
                        
                        if bet == 'baccarat':
                            s6 = self.search_element(driver, 'results', bet, 'super6 chip', status=True)
                            
                            if not s6:
                                total_winnings += float(chip.text.replace(',','')) * winning_odds
                            else:
                                odds['BANKER'] = 1
                                winning_odds = odds[bet_area.text.strip()]
                                
                                if bet_area.text == 'BANKER':
                                    if playerPoints <= 5 and bankerPoints == 6:
                                        total_winnings += (chipValue / 2)
                                    else:
                                        total_winnings += chipValue * winning_odds
                                else:
                                    total_winnings += chipValue * winning_odds

                        if bet == 'dragontiger':
                            getOdds = self.search_element(driver, 'in-game', 'dt-tie')
                            odds['TIE'] = getOdds.text.split(':')[1]
                            total_winnings += float(chip.text.replace(',','')) * winning_odds

                return total_winnings

            for win in win_results:
                area = self.utils.data('in-game', 'bet area title')
                side = self.utils.data('in-game', 'sidebet chips')
                main = self.utils.data('in-game', 'main bet chips')

                betNames = win.find_elements(By.CSS_SELECTOR, area)
                sideChips = win.find_elements(By.CSS_SELECTOR, side)
                mainChips = win.find_elements(By.CSS_SELECTOR, main)

                winnings += calculate_winnings(mainChips, betNames)
                winnings += calculate_winnings(sideChips, betNames)

            for lose in lose_results:
                side = self.utils.data('in-game', 'sidebet chips')
                main = self.utils.data('in-game', 'main bet chips')
                sideChips = lose.find_elements(By.CSS_SELECTOR, side)
                mainChips = lose.find_elements(By.CSS_SELECTOR, main)

                for chips in sideChips:
                    chipValue = float(chips.text.replace(',','')) if chips.text != '' else 0
                    print(f'loss sidechips: {chipValue}')
                    loss += chipValue

                for bets in mainChips:
                    betValue = float(bets.text.replace(',','')) if bets.text != '' else 0
                    print(f'loss mainChips: {betValue}')
                    loss += betValue

            for tie in win_results:
                area = self.utils.data('in-game', 'bet area title')
                betNames = tie.find_elements(By.CSS_SELECTOR, area)

                for names in betNames:
                    if bet == 'baccarat':
                        if names.text.strip() == 'TIE':
                            player = self.search_element(driver, 'results', bet, 'player chip')
                            banker = self.search_element(driver, 'results', bet, 'banker chip')
                            playerChips = float(player.text.replace(',','')) if player.text != '' else 0
                            bankerChips = float(banker.text.replace(',','')) if banker.text != '' else 0
                            print(f'TIE p: {playerChips} b: {bankerChips}')
                            loss -= playerChips + bankerChips

                    if bet == 'dragontiger':
                        player = self.search_element(driver, 'results', bet, 'player chip')
                        banker = self.search_element(driver, 'results', bet, 'banker chip')
                        playerChips = float(player.text.replace(',','')) if player.text != '' else 0
                        bankerChips = float(banker.text.replace(',','')) if banker.text != '' else 0
                        loss -= (playerChips + bankerChips) / 2

            postBalance = self.search_element(driver, 'in-game', 'balance')
            newBalance = float(postBalance.text.replace(',',''))
            result = balance + (winnings - loss)
            
            print(f'balance: {balance}')
            print(f'winloss: {winnings - loss}')
            print(f'win: {winnings} loss: {loss}')
            
            message = self.utils.debuggerMsg(tableDealer, f'Result Calculation {int(Decimal(result))} & '\
            f'Post Balance {int(Decimal(newBalance))} - [{Decimal(result):.2f}, {Decimal(newBalance):.2f}]')
            self.utils.assertion(message, f'{int(Decimal(result))}', '==', f'{int(Decimal(newBalance))}')

    def card_flips(self, driver, tableDealer, results: list[bool]):
        decode_and_status = [[], []]
        blue = self.search_elements(driver, 'in-game', 'result-card-blue')
        red = self.search_elements(driver, 'in-game', 'result-card-red')
        self.decoder.base64_encoded(blue, 'style', decode_and_status[0])
        self.decoder.base64_encoded(red, 'style', decode_and_status[0])
        card = self.decoder.decode_base64_card(decode_and_status[0], decode_and_status[1])
        driver.save_screenshot(f'screenshots/Card Results {tableDealer[0]} {self.utils.getUuid()}.png')

        card_metadata = [[],[],[],[]]
        if self.utils.env('table') in tableDealer[0]:
            ai_cards = self.search_elements(driver, 'in-game', 'result-dealer')
            self.decoder.base64_encoded(ai_cards, 'style', card_metadata[0])
            for base in card_metadata[0]:
                if len(base) < 2100:
                    card_metadata[1].append(base)

            dealer_cards = self.decoder.decode_base64_card(card_metadata[1], card_metadata[2])
            with open('logs\\logs.txt', 'a') as logs:
                logs.write(f'{tableDealer[0]} -- Digital Card {card} {self.utils.env("table")} Card {dealer_cards} \n')

            if len(dealer_cards) != 0:
                dealer_cards_count = Counter(dealer_cards)
                card_count = Counter(card)
                message = self.utils.debuggerMsg(tableDealer, f'\033[93mResult & {self.utils.env("table")} Dealer Cards Count - Expected: EQUAL')
                self.utils.assertion(message, dealer_cards_count, '==', card_count, notice=True)
                card_metadata[3].append(True)

            return results.append(all(card_metadata[3]))
        else:
            return results.append(all(decode_and_status[1]))
