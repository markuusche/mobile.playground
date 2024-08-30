import uuid
uuid = uuid.uuid1().hex

from src.helpers.helpers import Helpers
from src.utils.utils import Utilities
from src.utils.decoder import Decoder
from collections import Counter

class Results(Helpers):
    
    def __init__(self) -> None:
        super().__init__()
        self.decoder = Decoder()
        self.utils = Utilities()
        
    def win_lose(self, driver):
        """
        check the outcome of the game, whether it's a win or a loss.

        params:
        `driver` (webdriver): the selenium webdriver instance.

        : wait for the result toast element to appear in the in-game view using `waitelement`.
        : find and extract the win/loss result from the game using `findelement`.
        : if '-' is present in the result text, it indicates a loss.
        : in this case, extract the amount lost from the result text, convert it to a float, and format it
        : to display 'Lose: {amount}' with two decimal places.
        : otherwise, if '+' is present in the result text, it indicates a win.
        : in this case, extract the amount won from the result text, convert it to a float, and format it
        : to display 'Win: {amount}' with two decimal places.
        """

        self.wait_element(driver, 'in-game', 'resultToast')
        result = self.search_element(driver, 'in-game', 'resultToast')
        if '-' in result.text:
            get_result_amount = result.text.replace('Lose', '').replace('-','').replace(' ','').replace(',','')
            parse_amount = float(get_result_amount)
            return f'Lose: {parse_amount:.2f}'
        else:
            get_result_amount = result.text.replace('Win', '').replace('+','').replace(' ','').replace(',','')
            parse_amount = float(get_result_amount)
            return f'Win: {parse_amount:.2f}'

    def card_flips(self, driver, tableDealer, results: list[bool]):
        decode_and_status = [[], []]
        blue = self.search_elements(driver, 'in-game', 'result-card-blue')
        red = self.search_elements(driver, 'in-game', 'result-card-red')
        self.decoder.base64_encoded(blue, 'style', decode_and_status[0])
        self.decoder.base64_encoded(red, 'style', decode_and_status[0])
        card = self.decoder.decode_base64_card(decode_and_status[0], decode_and_status[1])
        driver.save_screenshot(f'screenshots/Card Results {tableDealer[0]} {uuid[:4]}.png')

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
