import random

from src.utils.utils import Utilities
from src.helpers.helpers import Helpers
from src.components.chips import Chips
from src.components.display import Display
from src.components.results import Results
from selenium.common.exceptions import ElementClickInterceptedException

class Betting(Helpers):

    def __init__(self) -> None:
        super().__init__()
        self.chips = Chips()
        self.display = Display()
        self.results = Results()
        self.utils = Utilities()

    def sidebets(self, driver, game, getIndex, bettingArea=None):
        """
        Determines and returns a side bet value based on the specified game.

        This function handles side bets for two games: 'dragontiger' and 'baccarat'.
        - For 'dragontiger', it checks the current round number and, if it's 29 or lower, 
        randomly selects a side bet from available options.
        - For 'baccarat', it checks for the presence of a specific betting area ('S6') 
        and, if found, includes it in the side bets available for selection.

        Parameters:
            driver: WebDriver instance used to interact with the web page.
            game (str): The game for which the side bet is to be determined ('dragontiger' or 'baccarat').
            getIndex (int): Index to retrieve a specific betting area from the provided list.
            bettingArea (list, optional): List of betting areas. Default is None.

        Returns:
            str: A randomly selected side bet value or a specified side bet based on the game's context.
        """

        sidebet = self.utils.data(game)
        if game == 'dragontiger':
            shoe = self.search_element(driver, 'in-game', 'shoe')
            tableRound = int(shoe.text.split('-')[1])
            if tableRound <= 29:
                sidebet.update(self.utils.data('sidebet', 'dragontiger'))
                bet_areas = list(sidebet)
                index = random.choice(range(len(bet_areas)))
                return sidebet[bet_areas[index]]
            
        if game == 'baccarat':
            s6 = False
            bet_areas = self.search_elements(driver, 'in-game', 'bet area title')
            for bet in bet_areas:
                if bet.text.strip() == 'S6':
                    s6 = True
                    
            if s6:
                sidebet['S6'] = self.utils.data('super6', 's6')
                with_s6 = list(sidebet)
                index = random.choice(range(len(with_s6)))
                return sidebet[f'{with_s6[index]}']
            
        return self.utils.data(game, bettingArea[getIndex])
            
    def bet_minimum(self, driver, game, tableDealer):
        """bets the minimum amount allowed for each betting area in the specified game

        params:
        `driver`: the selenium webdriver instance.
        `game` (str): the name of the game
        `tableDealer`: A string containing information about the table and dealer.
        `allin` (bool, optional): flag indicating whether to go all-in, defaults to False

        : basically what this do is get the minimum bet of the bet area as well as
        : get the label of that minimum bet.
        : edits the chips according the extracted minumum bet of the table
        : then places a chip and confirms and verifies if it shows 'Below minimum bet' else
        : assertion will fail
        """

        if game not in ['roulette', 'sicbo']:
            balance = self.search_element(driver, 'in-game', 'balance')
            user_balance = float(balance.text.replace(',',''))
            if user_balance != 0.00:
                def getElementText(selector):
                    return selector.text

                def popItem(listItem: list[int]):
                    index = listItem
                    index.reverse()
                    for item in index:
                        minimumBets.pop(item)
                        betNames.pop(item)

                self.wait_clickable(driver, 'in-game', 'payrate-modal')
                self.wait_element(driver, 'in-game', 'modal-bet')

                if game == 'sedie':
                    self.utils.customJS(driver , 'sedieBeads();')

                minmax = self.search_elements(driver, 'in-game', 'min-max')
                betLabel = self.search_elements(driver, 'in-game', 'limit label')

                minimumBets, betNames = [[],[]]
                for minimum, textLabel in zip(minmax, betLabel):
                    #get element texts
                    mmax = getElementText(minimum)
                    bLabel = getElementText(textLabel)

                    #filter the text
                    getMinBet = mmax.split(' -')[0].strip()
                    if game == 'bull bull':
                        for _ in range(3):
                            minimumBets.append(getMinBet)
                    else:
                        minimumBets.append(getMinBet)

                    if game == 'bull bull':
                        label = bLabel.replace('-','').replace(' ','', 1)
                        betNames.append(label)
                        betNames.append(f'{label} 2')
                        betNames.append(f'{label} 3')
                    else:
                        label = bLabel.find('(')
                        getLabel = bLabel[:label]
                        betNames.append(getLabel)

                #remove not needed bets
                if game == 'baccarat':
                    index = [5,6,9,10]
                    popItem(index)

                elif game == 'dragontiger':
                    shoe = self.search_element(driver, 'in-game', 'shoe')
                    try:
                        tableRound = int(shoe.text.split('-')[1])
                    except IndexError:
                        self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                        tableRound = int(shoe.text.split('-')[1])
                        
                    if tableRound <= 29:
                        index = [3,4,7,8]
                    else:
                        index = [3,4,5,6,7,8,9,10]

                    popItem(index)

                newData = {}
                for key, value in zip(minimumBets, betNames):
                    newData[value] = key

                self.wait_clickable(driver, 'in-game', 'payrate-close')
                self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                #start betting minimum bets
                bets = list(newData)
                for bet in range(len(bets)):
                    sidebet = self.utils.data(game)
                    getMin = newData[bets[bet]].split(' ')[0]
                    amount = int(getMin) - 1
                    self.chips.edit_chips(driver, add=True, amount=amount)
                    timer = self.search_element(driver, 'in-game', 'timer')
                    try:
                        if timer.text == 'CLOSED':
                            self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                        elif int(timer.text) <= 3:
                            self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                    except:
                        self.wait_element_invisibility(driver, 'in-game', 'toast')

                    if game == 'baccarat' and 'S6' in bets:
                        sidebet['S6'] = self.utils.data('super6', 's6')
                        betS6 = list(sidebet)
                        betAction = sidebet[f'{betS6[bet]}']
                    elif game == 'dragontiger':
                        if len(bets) > 3:
                            sidebet.update(self.utils.data('sidebet', 'dragontiger'))
                            newBetArea = list(sidebet)
                            betAction = sidebet[f'{newBetArea[bet]}']
                        else:
                            betAction = self.utils.data(game, bets[bet])
                    else:
                        betAction = self.utils.data(game, bets[bet])

                    self.utils.customJS(driver, f'click("{betAction}");')
                    self.utils.customJS(driver, f'click("{self.utils.data("action", "confirm")}");')

                self.utils.screenshot(driver, 'Minimum Bets', tableDealer[0])
                bet_area_chips = self.chips.get_chip_value(driver)
                message = self.utils.debuggerMsg(tableDealer, 'Minimum Bet Betting')
                self.utils.assertion(message, bet_area_chips, '==', 0)

                if game == 'bull bull':
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            else:
                message = self.utils.debuggerMsg(tableDealer, 'Not Enough Balance to Place a Chip')
                self.utils.assertion(message, skip=True)
        
            timer = self.search_element(driver, 'in-game', 'timer')
            try:
                if int(timer.text) <= 5:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            except:
                    self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')

    def betting(self, driver, betArea, game, placeConfirm=False):
        """
        place bets in the specified game's betting area(s).

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `betarea` (list): a list of bet areas.
        `game` (str): the name of the game.
        `placeconfirm` (bool, optional): whether to confirm the bet placement. default is false.

        : wait for the 'please place your bet!' toast message to appear in the in-game view using `waitpresence`.
        : set the loop range based on the game type: 10 for 'sicbo' and 'roulette', or the length of `betarea` for other games.
        : randomly choose whether to place a super 6 bet for baccarat if `placeconfirm` is true.
        : loop through the specified number of rounds (loopRange) to place bets in the game's betting areas.
        : use the `dtsidebet` function to generate the bet for each round and attempt to click on the corresponding betting area.
        : if `placeconfirm` is true, wait for the 'confirm' button to become clickable after placing each bet.
        """

        loopRange = 10 if game in ['sicbo', 'roulette'] else len(betArea)
        s6 = random.choice(range(2))
        if placeConfirm:
            if s6 == 1 and game == 'baccarat':
                self.wait_clickable(driver, 'super6', 'r-area')
                self.wait_element(driver, 'super6', 's6')
                self.wait_clickable(driver, 'super6', 's6')

        i = 0
        while i < loopRange:
            index = random.choice(range(len(betArea)))
            bets = self.sidebets(driver, game, index, bettingArea=betArea)
            try:
                self.utils.customJS(driver, f'click(`{bets}`);')
                if placeConfirm:
                    self.utils.customJS(driver, f'click(`{self.utils.data("action", "confirm")}`);')

                i += 1
            except ElementClickInterceptedException:
                break

    def cancel_rebet(self, driver, betArea, tableDealer, game, results):
        """
        cancel the bet placement action and perform necessary assertions.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `game` (str): the name of the game.
        `tabledealer` (string): a string containing information about the table and dealer.
        `allin` (bool): whether the player is in an 'all-in' situation.
        `texts` (str): text description for debugging.

        : wait for the 'cancel' button to become clickable in the action panel using `wait_if_clickable`.
        : take a screenshot of the game table with the specified text description using `screenshot`.
        : calculate the sum of all bets placed on the game table using `sumbetplaced`, indicating a cancellation action.
        """

        def assert_cancelled_bet(driver, game, tableDealer, texts):
            self.wait_clickable(driver, 'action', 'cancel')
            self.utils.screenshot(driver, texts, tableDealer[0])
            self.display.sum_of_placed_bets(driver, game, tableDealer, cancel=True, text=texts)

        def card_flipped(driver, game, tableDealer, results):
            if game in ['baccarat', 'dragontiger', 'three-cards', 'bull bull']:
                self.wait_text_element(driver, 'in-game','toast', text='No More Bets!')
                self.wait_element_invisibility(driver, 'in-game', 'toast')
                self.wait_element(driver, 'in-game', 'toast')
                self.results.card_flips(driver, tableDealer, results)

        if game == 'bull bull':
            self.chips.edit_chips(driver, 30)
            
        self.betting(driver, betArea, game)
        chips = self.chips.get_chip_value(driver)
        message = self.utils.debuggerMsg(tableDealer, '\033[93mChips are being placed.')
        self.utils.assertion(message, chips, '>', 0, notice=True)

        assert_cancelled_bet(driver, game, tableDealer, 'Chip placed & cancelled!')
        self.betting(driver, betArea, game, placeConfirm=True)
        card_flipped(driver, game, tableDealer, results)
        self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
        self.wait_clickable(driver, 'action', 'rebet')

        insufficient = self.utils.customJS(driver, 'toast_check("Insufficient funds to rebet!");')
        message = self.utils.debuggerMsg(tableDealer, 'Insufficient funds to rebet!')
        if insufficient:
            self.utils.assertion(message, skip=True)
        else:
            assert_cancelled_bet(driver, game, tableDealer, 'Rebet & Cancelled!')
            self.wait_clickable(driver, 'action', 'rebet')
            self.utils.customJS(driver, f'click(`{self.utils.data("action", "confirm")}`);')
            self.utils.screenshot(driver, 'Rebet & Confirmed!', tableDealer[0])
            card_flipped(driver, game, tableDealer, results)
            
    def allin_bet(self, driver, game, results):
        """
        handle the scenario where the player bets all their coins in the game.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `game` (str): the name of the game.
        `allin` (bool, optional): whether the player is going all-in. default is false.

        : generate a list of betting areas for the specified game using the `data` function.
        : retrieve information about the table and dealer using the `table_dealer` function.
        : cancel any rebets, if present, using the `cancelrebet` function.
        : edit the chip amount using the `editchips` function.
        : enter a loop to place bets until the player has bet all their coins.
        : check if there are sufficient funds to place a bet. if not, take necessary actions,
        : such as taking a screenshot, confirming, or handling specific game cases.
        : if the game is 'bull bull', handle a special case where an 'equal' bet is placed
        : if there are insufficient funds. verify that the player's balance is now 0.00 after going all-in.
        : check if there are leftover chips the table betting area using the `sumbetplaced` function.
        """

        bet_areas = list(self.utils.data(game))
        tableDealer = self.table_dealer(driver)
        self.cancel_rebet(driver, bet_areas, tableDealer, game, results)
        self.bet_minimum(driver, game, tableDealer)
        self.chips.edit_chips(driver)

        while True:
            coins = self.search_element(driver, 'in-game','balance')
            index = random.choice(range(len(bet_areas)))
            bets = self.sidebets(driver, game, index, bettingArea=bet_areas)
            try:
                self.utils.customJS(driver, f'click(`{bets}`);')
            except ElementClickInterceptedException:
                self.wait_text_element(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                self.utils.customJS(driver, f'click(`{bets}`);')

            insufficient = self.utils.customJS(driver, 'toast_check("Insufficient Balance");')

            if insufficient:
                self.utils.screenshot(driver, 'Insufficient Balance', tableDealer[0])
                self.utils.customJS(driver, f'click(`{self.utils.data("action", "confirm")}`);')
                self.wait_element_invisibility(driver, 'in-game', 'toast')

                if game == 'bull bull':
                    equalBet = []
                    coins = self.search_element(driver, 'in-game','balance')
                    for bet in bet_areas:
                        if 'EQUAL' in bet:
                            equalBet.append(bet)

                    while True:
                        coins = self.search_element(driver, 'in-game','balance')
                        if coins.text != '0.00':
                            randomSelect = random.choice(range(len(equalBet)))
                            self.utils.customJS(driver, f'click("{self.utils.data(game, equalBet[randomSelect])}");')
                            insufficient = self.utils.customJS(driver, 'toast_check("Insufficient Balance");')

                            if insufficient:
                                self.utils.customJS(driver, f'click("{self.utils.data("action", "confirm")}");')
                        else: break
                else:
                    self.wait_text_element(driver, 'in-game', 'balance', text='0.00', timeout=10)
                break

        message = self.utils.debuggerMsg(tableDealer, f'All-in bet {coins.text}')
        self.utils.assertion(message, coins.text, '==', '0.00')
        self.display.sum_of_placed_bets(driver, game, tableDealer)

    def payrates_odds(self, driver, game, tableDealer):
        """
        verify pay rates and odds

        params:
        `driver` (webdriver): the selenium WebDriver instance.
        `game` (str): the name of the game.
        `tabledealer` (str): A string containing information about the table and dealer.
        `allin` (bool, optional): flag indicating if the player is going all-in. Default is False.

        : retrieve the bet limit for the specified game using the `data` function.
        : wait for the payrate modal to be clickable and the modal-bet element to be present.
        : take a screenshot of the bet limit and pay rate.
        : extract the pay rates for the game from the web page.
        : if the game is 'baccarat' and super6 side bet is present, adjust the odds accordingly.
        : if the game is 'sedie', extract the pay rates for sedie games.
        : if the game is 'dragontiger' and the table number matches, adjust the odds accordingly.
        : verify that the bet limit rate and local bet limit rate are equal.
        : if the game is 'bull bull', take a screenshot of the bet limit with min-max values.
        : extract min-max limit elements and verify that they are all displayed.
        : close the payrate modal.
        """

        if game != 'bull bull':
            odds, game_odds = [[],[]]
            betLimit = self.utils.data('bet-limit').get(game)
            for _, item in betLimit.items():
                odds.append(item)

            self.wait_clickable(driver, 'in-game', 'payrate-modal')
            self.wait_element(driver, 'in-game', 'modal-bet')
            self.utils.screenshot(driver, 'BET Limit - Payrate', tableDealer[0])
            payrates = self.search_elements(driver, 'in-game', 'payrates')
            sedie_payrates = self.search_elements(driver, 'in-game', 'sedie-payrate')
            super6 = self.search_elements(driver, 'super6', 's6')

            for payrate in payrates:
                game_odds.append(payrate.text)

            if game == 'baccarat' and len(super6) == 1:
                odds.append('(1:12)')
                odds[1] = '(1:1)'

            elif game == 'sedie':
                for payrate in sedie_payrates:
                    game_odds.append(payrate.text)

            elif game == 'dragontiger':
                tableNumbers = self.utils.env('newDT').split(':')
                if tableDealer[0] in tableNumbers:
                    odds[2] = '(1:8)'

            message = self.utils.debuggerMsg(tableDealer, f'Equal Bet limit rate & Local bet limit rate')
            self.utils.assertion(message, odds, '==', game_odds)

        else:
            self.wait_clickable(driver, 'in-game', 'payrate-modal')
            self.wait_element(driver, 'in-game', 'modal-bet')
            self.utils.screenshot(driver, 'BET Limit - MinMax', tableDealer[0])

        minMaxLimit = self.search_elements(driver, 'in-game', 'min-max')
        value = []
        for limit in minMaxLimit:
            if len(limit.text) != 0 or limit.text is not None or limit.text != '':
                value.append(True)
            else:
                value.append(False)

        message = self.utils.debuggerMsg(tableDealer, f'Bet limit min-max are all displayed')
        self.utils.assertion(message, all(value))
        self.wait_clickable(driver, 'in-game', 'payrate-close')
        self.wait_element_invisibility(driver, 'in-game', 'modal-bet')