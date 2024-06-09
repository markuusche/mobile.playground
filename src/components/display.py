import re

from src.utils.utils import Utilities
from src.helpers.helpers import Helpers
from src.components.chips import Chips

class Display(Helpers):

    def __init__(self) -> None:
        super().__init__()
        self.chips = Chips()
        self.utils = Utilities()
 
    def digital_result(self, driver, bet, tableDealer):
        """
        verify the absence of new round digital results and the status of placed chips

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `bet` (str): the name of the game.
        `tableDealer` (str): A string containing information about the table and dealer.

        : defines a nested function `verify_digitalresult` to check if digital
        : results are displayed for a new round.
        : determines the game type and verifies digital results accordingly.
        : if the game type is 'baccarat', 'three-cards', 'dragontiger', or 'bull bull',
        : checks for the absence of digital results.
        : for 'sicbo' and 'roulette' games, verifies the absence of digital results.
        : checks the status of placed chips after the new round and ensures that no chips are placed.

        """

        def verify_digital_result(driver, game, tableDealer):
            digital = self.search_element(driver, 'digital results', game)
            message = self.utils.debuggerMsg(tableDealer, 'New Round Digital Result was not displayed!')
            self.utils.assertion(message, digital.is_displayed(), '==', False)

        if bet in ['baccarat', 'three-cards', 'dragontiger', 'bull bull']:
            verify_digital_result(driver, 'bdt', tableDealer)
        elif bet == 'sicbo':
            verify_digital_result(driver, 'sicbo', tableDealer)
        elif bet == 'roulette':
            verify_digital_result(driver, 'roulette', tableDealer)
        else:
            self.wait_element_invisibility(driver, 'digital results', 'sedie', \
            timeout=3, isDigital=True, tableDealer=tableDealer)

        self.sum_of_placed_bets(driver, bet, tableDealer, cancel=True, text='No placed chips after new round')
        
    def roadmap_summary(self, driver, game, tableDealer):
        """
        Retrieve and verify the summary information for the specified game.

        params:
        `driver` (webdriver): The Selenium WebDriver instance.
        `game` (str): The name of the game for which the summary information is to be retrieved and verified.
        `tabledealer` (string): A string containing information about the table and dealer.

        : This function calculates the total summary value based on the numeric values extracted from summary elements on the page.
        : For certain games like 'sedie', it clicks on side buttons to reveal additional summaries.
        : Finally, it verifies that the total summary matches the round number displayed in the shoe element minus one.
        """

        if game != 'bull bull':
            total = 0
            if game not in ['sicbo', 'roulette']:
                if game == 'baccarat' or 'dragontiger':
                    summaries = self.search_elements(driver, 'in-game', 'summary')

                if game == 'sedie':
                    summaries = self.search_elements(driver, 'in-game', 'sedie-summary')
                    sideBtn = self.search_elements(driver, 'in-game', 'sedie-sidebtn')
                    for buttons in sideBtn[::-1]:
                        buttons.click()

                for index, element in enumerate(summaries):
                    if game == 'three-cards' and index == 3:
                        continue
                    if game == 'sedie' and index != 2 and index != 3:
                        continue

                    match = re.search(r'\d+', element.text)
                    if match:
                        number = int(match.group())
                        total += number

                while True:
                    shoe = self.search_element(driver, 'in-game', 'shoe')
                    if shoe.text == '' or shoe.text == None:
                        self.wait_text_element(driver, 'in-game','toast', text='Please Place Your Bet!')
                        continue
                    else:
                        if game in ['three-cards', 'sedie']:
                            value = int(shoe.text)
                        else:
                            value = int(shoe.text.split('-')[1])
                        break

                message = self.utils.debuggerMsg(tableDealer, f'Roadmap total {total}, '\
                f'Shoe round {value} - Expected: round > total')
                self.utils.assertion(message, total, '==', value -1)
                
    def roulette_race_tracker(self, driver, tableDealer):
        """
        check if the race tracker is displayed.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `tabledealer` (string): a string containing information about the table and dealer.

        : click on the switch button to toggle to the race tracker view.
        : wait for the race tracker element to be visible.
        : verify that the race tracker is displayed.
        : click on the switch button again to switch back to the main view.
        : assert if the racetracker is displayed
        """

        self.search_element(driver, 'in-game', 'switch', click=True)
        self.wait_element(driver, 'in-game', 'race-tracker', timeout=3)
        raceTracker = self.search_element(driver, 'in-game', 'race-tracker')
        message = self.utils.debuggerMsg(tableDealer, 'Race Tracker is displayed.')
        self.utils.assertion(message, raceTracker.is_displayed(), '==', True)
        self.search_element(driver, 'in-game', 'switch', click=True)
        
    def sum_of_placed_bets(self, driver, game, tableDealer, cancel=False, text=None):
        """
        check the status of placed bets

        params:
        `driver` (webdriver): the selenium WebDriver instance.
        `game` (str): the name of the game.
        `tabledealer` (str): A string containing information about the table and dealer.
        `cancel` (bool, optional): flag to determine if bets should be canceled. Default is False.
        `text` (str, optional): additional text for debugging. Default is None.

        : check the current chip value using the `getChipValue` function.
        : if `cancel` is True, verify that no chips are placed.
        : if `cancel` is False, compare the total placed chips with the expected value.
        : if the game is not 'bull bull', retrieve the total placed bets and compare them with the expected value.
        """

        chips = self.chips.get_chip_value(driver)
        total = 0.00

        if cancel:
            message = self.utils.debuggerMsg(tableDealer, f'{text} {chips} - Expected: No chips placed')
            self.utils.assertion(message, chips, '==', 0)
        else:
            if game != 'bull bull':
                bets = self.search_element(driver, 'in-game', 'bets')
                if bets != None:
                    total = float(bets.text.replace(',',''))
                    message = self.utils.debuggerMsg(tableDealer, f'Placed chips {round(chips, 2)} '\
                    f'& Bets {total} - Expected: EQUAL')
                    self.utils.assertion(message, round(chips, 2), '==', total)
                else:
                    message = self.utils.debuggerMsg(tableDealer, f'\033[91m"Bets:" is empty, cannot confirm and '\
                    f'compare chips value with the placed chips\033[0m')
                    self.utils.assertion(message, skip=True)
