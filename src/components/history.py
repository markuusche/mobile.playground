from src.utils.utils import Utilities
from src.utils.decoder import Decoder
from src.helpers.helpers import Helpers

class History(Helpers):

    def __init__(self) -> None:
        super().__init__()
        self.decode = Decoder()
        self.utils = Utilities()

    def bet_history(self, driver, game, status, cardResults, extracted):
        """
        retrieve and process the bet history data for the specified game.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `game` (str): the name of the game.
        `status` (list): an empty list to store the status of each decoded image.
        `card_results` (int): the number of card results obtained previously.
        `extracted` (int): the number of card images extracted previously.

        : if the game is not one of ['sedie', 'sicbo', 'roulette']:
        : find and extract base64 encoded images for blue and red cards from the bet history.
        : determine the selector and attribute based on the game.
        : update the card results count with the number of blue and red cards found.
        : remove empty strings from the extracted blue and red card base64 sequences.
        : decode and crop the images to extract card values.
        : update the total number of extracted card values.
        : delete the temporary images.

        returns: the extracted card values, updated flipped card count, and total extracted card count.
        """

        if game not in ['sedie', 'sicbo', 'roulette']:
            blue_card_value, red_card_value = [[],[]]
            selector = 'result-blue' if game != 'bull bull' else 'result-blue-bull'
            blueCards = self.search_elements(driver, 'history', selector)
            redCards = self.search_elements(driver, 'history', 'result-red')
            atrribute = 'class' if game != 'bull bull' else 'style'
            self.decode.base64_encoded(blueCards, atrribute, blue_card_value)
            self.decode.base64_encoded(redCards, 'class', red_card_value)
            flipped_cards = cardResults + len(blue_card_value + red_card_value)
            #remove empty strings
            new_item, _new_item, newDecode = [[],[],[]]

            #repeated loop to get cards base64 sequence same as the results
            for blue in blue_card_value:
                if blue.strip():
                    new_item.append(blue)

            for red in red_card_value:
                if red.strip():
                    _new_item.append(red)

            for item in new_item:
                if 'card-hidden' not in item:
                    newDecode.append(item)

            for item2 in _new_item:
                if 'card-hidden' not in item2:
                    newDecode.append(item2)

            card = self.decode.decode_base64_card(newDecode, status)
            cardData = extracted + len(new_item + _new_item)
            self.utils.deleteImages('screenshots\\decoded')

            return card, flipped_cards, cardData

    def open_bet_history(self, driver, game, tableDealer, oldRow=0, updates=False):
        """
        open the bet history modal in the game interface and retrieves the transaction data

        params:
        `driver` (webdriver): The Selenium WebDriver instance.
        `game` (str): The name of the game.
        `tableDealer` (str): a string containing information about the table and dealer.
        `oldRow` (int, optional): The number of rows in the bet history before updates. Default is 0.
        `updates` (bool, optional): Flag indicating if updates are expected. Default is False.

        : clicks on the bet history button to open the modal and waits for it to appear.
        : filters the bet history by the specified game if it's not in ['sedie', 'sicbo', 'roulette'].
        : scrolls to the top of the transaction data table after scrolling to last transaction.
        : ff updates are expected, checks for new rows in the bet history, retrieves and processes the details.
        : logs details of each row for debugging purposes.
        : verifies the decoded base64 image and extracted card values, if available.
        : closes the bet history modal after processing.
        : returns the total number of rows in the bet history.
        """

        if game not in ['sedie', 'sicbo', 'roulette']:
            self.wait_clickable(driver, 'history', 'button')
            self.wait_element(driver, 'history', 'modal')
            selectGame = self.utils.data('history', 'filter')
            gameIndex = self.utils.data('game list', game)
            self.utils.customJS(driver, f'selectGameList("{selectGame}", {gameIndex})')
            expand = self.search_element(driver, 'history', 'expand', status=True)
            
            try:
                while expand.is_displayed():
                    self.wait_clickable(driver, 'history', 'expand', timeout=3)
            except:
                ...

            self.wait_element_invisibility(driver, 'history', 'expand')
            countRows = self.search_elements(driver, 'history', 'detail')
            if len(countRows) != 0 and updates:
                status = []
                flipped_cards = 0
                extracted = 0
                rowsAdded = len(countRows) - oldRow
                message = self.utils.debuggerMsg(tableDealer, f'Bet History {rowsAdded} new rows has been added')
                self.utils.assertion(message, len(countRows), '>', oldRow, notice=True)
                dataTable = self.search_element(driver, 'history', 'data table')
                detail = self.search_elements(driver, 'history', 'detail')
                tableStage = self.search_elements(driver, 'history', 'table')
                driver.execute_script("arguments[0].scrollTop = 0;", dataTable)

                for rows in range(rowsAdded):
                    detail[rows].click()
                    getTable = tableStage[rows].text
                    self.wait_element(driver, 'history', 'result')
                    baseList, flipped_cards, extracted = self.bet_history(driver, game, status, flipped_cards, extracted)
                    #creates log history for debugging in case of failure
                    with open('logs\\logs.txt', 'a') as logs:
                        newLine = '\n'
                        logs.write(f'Index {rows} {getTable.replace(f"{newLine}"," ")} -'\
                        f'Cards {baseList} {newLine} ')

                    self.wait_clickable(driver, 'history', 'close card')
                    self.wait_element_invisibility(driver, 'history', 'result')

                if len(status) != 0:
                    if all(status):
                        message = self.utils.debuggerMsg(tableDealer, f'Decoded Cards {flipped_cards} & '\
                        f'Extracted Values {extracted} - Expected - EQUAL ')
                        self.utils.assertion(message, flipped_cards, '==', extracted)
                    else:
                        message = self.utils.debuggerMsg(tableDealer, 'One or more extracted card data '\
                        f'was not in the list of cards')
                        self.utils.assertion(message, notice=True)
                else:
                    message = self.utils.debuggerMsg(tableDealer, 'History results is empty!')
                    self.utils.assertion(message, notice=True)

            self.wait_clickable(driver, 'in-game', 'payrate-close')
            self.wait_element_invisibility(driver, 'history', 'modal')
            
            return len(countRows)

