from src.libs.modules import *
from src.utilities.utilities import Utilities
from src.request.api import Requests
from src import BET_LIMIT
class Chips(Utilities):
    def __init__(self) -> None:
        super().__init__()

    def getChipValue(self, driver):
        """
        calculate the total amount of chips placed on the game table.

        params:
        `driver` (webdriver): the selenium webdriver instance.

        : find all elements representing the total amount of money placed
        : on the game table using `findelements`.
        : loop through each element to extract the chip amount, remove any comma separators,
        : and convert it to a float. add up all the chip amounts to get the total.

        returns:
        :`float` the total amount of chips placed on the game table.
        """

        chips = 0.00
        placed_chips = self.findElements(driver, 'in-game', 'totalMoney')

        for chip in placed_chips:
            if chip.text != '':
                chips += float(chip.text.replace(',',''))

        return chips

    def editChips(self, driver, divideBy=10, add=False, amount=0, BET_LIMIT=0):
        """
        edit the chip amount in the game interface and return the updated chip value.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `divideby` (int, optional): the divisor used to calculate the new chip amount.
         default is 10.

        : find the current balance of chips on the game table using `findelement`.
        : extract the numerical value from the balance text, remove any comma separators,
        : and convert it to a float.
        : calculate the new chip amount by dividing the balance value by the specified divisor.
        : wait for the 'edit' button to become clickable in the in-game view using `wait_if_clickable`.
        : wait for the chip amount element to appear using `waitelement`.
        : wait for the 'edit' button to become clickable in the chip amount interface.
        : wait for the 'clear' button to become clickable in the chip amount interface.
        : locate the input field for entering the new chip amount using `findelement`.
        : enter the calculated chip amount into the input field.
        : wait for the 'save amount' button to become clickable.
        : wait for the 'payrate-close' button to become clickable.
        : wait for the chip modal to disappear from the interface.

        returns:
        `int`: the updated chip amount after editing.
        """

        bets = self.findElement(driver, 'in-game', 'balance')
        value = float(bets.text.replace(',',''))
        if add:
            chips = amount
        else:
            chips = int(value) / divideBy - 1
            if chips < BET_LIMIT:
                random_chip = random.randint(BET_LIMIT, BET_LIMIT+99)
                chips = random_chip

        self.wait_If_Clickable(driver, 'in-game', 'edit')
        self.waitElement(driver, 'in-game', 'chip amount')
        self.wait_If_Clickable(driver, 'in-game', 'edit button')
        self.wait_If_Clickable(driver, 'in-game', 'clear')
        input = self.findElement(driver, 'in-game', 'input chips')
        input.send_keys(int(chips))
        self.wait_If_Clickable(driver, 'in-game', 'save amount')
        self.wait_If_Clickable(driver, 'in-game', 'payrate-close')
        self.waitElementInvis(driver, 'in-game', 'chip amount')

class Display(Chips):
    def __init__(self) -> None:
        super().__init__()

    def verifiy_newRound(self, driver, bet, tableDealer):
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

        def verify_digitalResult(driver, game, tableDealer):
            digital = self.findElement(driver, 'digital results', game)
            message = self.debuggerMsg(tableDealer, 'New Round Digital Result not displayed!')
            self.assertion(message, digital.is_displayed(), '==', False)

        if bet in ['baccarat', 'three-cards', 'dragontiger', 'bull bull']:
            verify_digitalResult(driver, 'bdt', tableDealer)
        elif bet == 'sicbo':
            verify_digitalResult(driver, 'sicbo', tableDealer)
        elif bet == 'roulette':
            verify_digitalResult(driver, 'roulette', tableDealer)
        else:
            self.waitElementInvis(driver, 'digital results', 'sedie', \
            setTimeout=3, isDigital=True, tableDealer=tableDealer)

        self.sumBetPlaced(driver, bet, tableDealer, cancel=True, text='No placed chips after new round')

    def summary(self, driver, game, tableDealer):
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
                    summaries = self.findElements(driver, 'in-game', 'summary')

                if game == 'sedie':
                    summaries = self.findElements(driver, 'in-game', 'sedie-summary')
                    sideBtn = self.findElements(driver, 'in-game', 'sedie-sidebtn')
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
                    shoe = self.findElement(driver, 'in-game', 'shoe')
                    if shoe.text == '' or shoe.text == None:
                        self.waitPresence(driver, 'in-game','toast', text='Please Place Your Bet!')
                        continue
                    else:
                        if game in ['three-cards', 'sedie']:
                            value = int(shoe.text)
                        else:
                            value = int(shoe.text.split('-')[1])
                        break

                message = self.debuggerMsg(tableDealer, f'Rodmap total summary {total}, '\
                f'Shoe round {value} - Expected: round > total')
                self.assertion(message, total, '==', value -1)

    def check_raceTracker(self, driver, tableDealer):
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

        self.findElement(driver, 'in-game', 'switch', click=True)
        self.waitElement(driver, 'in-game', 'race-tracker', setTimeout=3)
        raceTracker = self.findElement(driver, 'in-game', 'race-tracker')
        message = self.debuggerMsg(tableDealer, 'Race Tracker is displayed.')
        self.assertion(message, raceTracker.is_displayed(), '==', True)
        self.findElement(driver, 'in-game', 'switch', click=True)

    def sumBetPlaced(self, driver, game, tableDealer, cancel=False, text=None):
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

        chips = self.getChipValue(driver)
        total = 0.00

        if cancel:
            message = self.debuggerMsg(tableDealer, f'{text} {chips} - Expected: No chips placed')
            self.assertion(message, chips, '==', 0)
        else:
            if game != 'bull bull':
                bets = self.findElement(driver, 'in-game', 'bets')
                if bets != None:
                    total = float(bets.text.replace(',',''))
                    message = self.debuggerMsg(tableDealer, f'Placed chips {round(chips, 2)} '\
                    f'& Bets {total} - Expected: EQUAL')
                    self.assertion(message, round(chips, 2), '==', total)
                else:
                    message = self.debuggerMsg(tableDealer, f'\033[91m"Bets:" is empty, cannot confirm and '\
                    f'compare chips value with the placed chips\033[0m')
                    self.assertion(message, skip=True)

class Decoder(Utilities):

    def __init__(self) -> None:
        super().__init__()

    def getBaseImage(self, cards, attribute, cardList):
        """
        Extract base64 encoded images from the given list of cards.

        params:
        `cards` (list): A list of card elements.
        `attribute` (str): The attribute to retrieve from the card elements.
        `cardlist` (list): An empty list to store the extracted base64 encoded images.

        : Iterate through the list of card elements.
        : Extract the specified attribute value from each card element.
        : If the attribute value indicates that the card is not hidden and contains a base64 encoded image,
        : extract the base64 encoded image and append it to the provided cardlist.
        """

        for card in cards:
            attValue = card.get_attribute(f'{attribute}')

            if 'card-hidden' not in attValue and 'base64' in attValue:
                pattern = r'iVBOR[^"]+'
                matches = re.findall(pattern, attValue)
                if matches:
                    base64 = matches[0]
                    cardList.append(base64)

    def decodeCropImage(self, decoded, status):
        """
        Decode and crop images from base64 encoded strings.

        params:
        `decoded` (list): A list of base64 encoded image strings.
        `status` (list): An empty list to store the status of each decoded image.

        : Iterate through the list of decoded base64 encoded image strings.
        : Decode each base64 encoded string and open it as an image.
        : Crop the image to a specific size.
        : Save the cropped image to a file.
        : Use Tesseract OCR to extract the text value from the cropped image.
        : Check if the extracted text value is present in the predefined list of cards.
        : Append the status of each card extraction to the status list.
        : Return a list of extracted card values.
        """

        card = []
        for index, baseString in enumerate(decoded):
            base = base64.b64decode(baseString)
            getImage = Image.open(BytesIO(base))
            size = (10, 0, 80, 65)
            resizeImage = getImage.crop(size)
            resizeImage.save(f'screenshots\\decoded\\card {index}.png')
            value = tess.image_to_string(Image.open(f'screenshots\\decoded\\card {index}.png'), config='--psm 10')
            if str(value.replace('\n','')) in str(self.data('cards')):
                status.append(True)
                card.append(str(value.replace('\n','')))
            else:
                print(str(value.replace('\n',''), 'card value that is not in data("cards")'))
                status.append(False)

        return card

class Results(Decoder):

    def __init__(self) -> None:
        super().__init__()

    def LoseOrWin(self, driver):
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

        self.waitElement(driver, 'in-game', 'resultToast')
        result = self.findElement(driver, 'in-game', 'winloss')
        if '-' in result.text:
            getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
            return f'Lose: {getText:.2f}'
        else:
            getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
            return f'Win: {getText:.2f}'

    def cardFlips(self, driver, tableDealer, results: list[bool]):
        decode_and_status = [[], []]
        blue = self.findElements(driver, 'in-game', 'result-card-blue')
        red = self.findElements(driver, 'in-game', 'result-card-red')
        self.getBaseImage(blue, 'style', decode_and_status[0])
        self.getBaseImage(red, 'style', decode_and_status[0])
        card = self.decodeCropImage(decode_and_status[0], decode_and_status[1])
        driver.save_screenshot(f'screenshots/Card Results {tableDealer[0]} {uuid[:4]}.png')

        card_metadata = [[],[],[],[]]
        if self.env('table') in tableDealer[0]:
            ai_cards = self.findElements(driver, 'in-game', 'result-dealer')
            self.getBaseImage(ai_cards, 'style', card_metadata[0])
            for base in card_metadata[0]:
                if len(base) < 2000:
                    card_metadata[1].append(base)

            dealer_cards = self.decodeCropImage(card_metadata[1], card_metadata[2])
            with open('logs\\logs.txt', 'a') as logs:
                logs.write(f'{tableDealer[0]} -- Digital Card {card} {self.env("table")} Card {dealer_cards} \n')

            if len(dealer_cards) != 0:
                message = self.debuggerMsg(tableDealer, f'\033[93mResult & {self.env("table")} Dealer Cards Count - Expected: EQUAL')
                self.assertion(message, len(dealer_cards), '==', len(card), notice=True)

                for deck in dealer_cards:
                    if deck in card:
                        card_metadata[3].append(True)

            return results.append(all(card_metadata[3]))
        else:
            return results.append(all(decode_and_status[1]))

class Betting(Display):

    def __init__(self) -> None:
        super().__init__()
        self.results = Results()
        self.decoder = Decoder()

    def dtSidebet(self, driver, game, getIndex, bettingArea=None):
        """
        generate a side bet for dragontiger game

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `game` (str): the name of the game.
        `betarea` (list, optional): a list of bet areas. default is None.

        : extract the table round number from the game's shoe element using `findelement` and
        : convert it to an integer. if the game is 'dragontiger', update the dragontiger dictionary
        : with side bet data. use the updated dictionary if the table round number is less than or equal to 30,
        : otherwise, return the default betting area.
        """

        if game == 'dragontiger':
            shoe = self.findElement(driver, 'in-game', 'shoe')
            tableRound = int(shoe.text.split('-')[1])
            if tableRound <= 30:
                sidebet = self.data(game)
                sidebet.update(self.data('sidebet', 'dragontiger'))
                bet_areas = list(sidebet)
                index = random.choice(range(len(bet_areas)))
                return sidebet[bet_areas[index]]
            
        return self.data(game, bettingArea[getIndex])

    def minBet(self, driver, game, tableDealer, allin=False):
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
            balance = self.findElement(driver, 'in-game', 'balance')
            parseBalance = float(balance.text.replace(',',''))
            if parseBalance != 0.00:
                def getElementText(selector):
                    return selector.text

                def popItem(listItem: list[int]):
                    index = listItem
                    index.reverse()
                    for item in index:
                        minimumBets.pop(item)
                        betNames.pop(item)

                self.wait_If_Clickable(driver, 'in-game', 'payrate-modal')
                self.screenshot(driver, 'Minimum Bets', tableDealer[0], allin)
                self.waitElement(driver, 'in-game', 'modal-bet')

                if game == 'sedie':
                    self.customJS(driver , 'sedieBeads();')

                minmax = self.findElements(driver, 'in-game', 'min-max')
                betLabel = self.findElements(driver, 'in-game', 'limit label')

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
                    shoe = self.findElement(driver, 'in-game', 'shoe')
                    tableRound = int(shoe.text.split('-')[1])
                    if tableRound <= 30:
                        index = [3,4,7,8]
                    else:
                        index = [3,4,5,6,7,8,9,10]

                    popItem(index)

                newData = {}
                for key, value in zip(minimumBets, betNames):
                    newData[value] = key

                self.wait_If_Clickable(driver, 'in-game', 'payrate-close')
                self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                #start betting minimum bets
                assertMin = []
                bets = list(newData)
                for bet in range(len(bets)):
                    sidebet = self.data(game)
                    amount = int(newData[bets[bet]]) - 1
                    self.editChips(driver, add=True, amount=amount)
                    timer = self.findElement(driver, 'in-game', 'timer')
                    try:
                        if int(timer.text) <= 3:
                            self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                    except:
                        self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

                    if game == 'baccarat' and 'S6' in bets:
                        sidebet['S6'] = self.data('super6', 's6')
                        betS6 = list(sidebet)
                        betAction = sidebet[f'{betS6[bet]}']
                    elif game == 'dragontiger':
                        if len(bets) > 3:
                            sidebet.update(self.data('sidebet', 'dragontiger'))
                            newBetArea = list(sidebet)
                            betAction = sidebet[f'{newBetArea[bet]}']
                        else:
                            betAction = self.data(game, bets[bet])
                    else:
                        betAction = self.data(game, bets[bet])

                    self.customJS(driver, f'click("{betAction}");')
                    self.customJS(driver, f'click("{self.data("action", "confirm")}");')
                    status = self.waitPresence(driver, 'in-game', 'toast', text='Below Minimum Limit', setTimeout=1.2)
                    if status:
                        assertMin.append(True)
                    else:
                        self.screenshot(driver, 'Minimum bet failed', tableDealer[0], allin)
                        print(f'[{tableDealer[0]}] Locator: {betAction}')
                        assertMin.append(False)

                message = self.debuggerMsg(tableDealer, 'Minimum Bet Betting')
                self.assertion(message, all(assertMin))
                if game == 'bull bull':
                    self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            else:
                message = self.debuggerMsg(tableDealer, 'Not Enough Balance to Place a Chip')
                self.assertion(message, skip=True)

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

        self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
        loopRange = 10 if game in ['sicbo', 'roulette'] else len(betArea)
        s6 = random.choice(range(2))
        if placeConfirm:
            if s6 == 1 and game == 'baccarat':
                self.wait_If_Clickable(driver, 'super6', 'r-area')
                self.waitElement(driver, 'super6', 's6')
                self.wait_If_Clickable(driver, 'super6', 's6')

        i = 0
        while i < loopRange:
            index = random.choice(range(len(betArea)))
            bets = self.dtSidebet(driver, game, index, bettingArea=betArea)
            try:
                self.customJS(driver, f'click(`{bets}`);')
                if placeConfirm:
                    self.customJS(driver, f'click(`{self.data("action", "confirm")}`);')

                i += 1
            except ElementClickInterceptedException:
                break

    def cancelRebet(self, driver, betArea, tableDealer, game, results, allin=False):
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

        def cancelAssert(driver, game, tableDealer, allin, texts):
            self.wait_If_Clickable(driver, 'action', 'cancel')
            self.screenshot(driver, texts, tableDealer[0], allin)
            self.sumBetPlaced(driver, game, tableDealer, cancel=True, text=texts)

        def card_flipped(driver, game, tableDealer, results):
            if game in ['baccarat', 'dragontiger', 'three-cards', 'bull bull']:
                self.waitPresence(driver, 'in-game','toast', text='No More Bets!')
                self.waitElementInvis(driver, 'in-game', 'toast')
                self.waitElement(driver, 'in-game', 'toast')
                self.results.cardFlips(driver, tableDealer, results)

        self.betting(driver, betArea, game)
        chips = self.getChipValue(driver)
        message = self.debuggerMsg(tableDealer, '\033[93mChips are being placed.')
        self.assertion(message, chips, '>', 0, notice=True)

        cancelAssert(driver, game, tableDealer, allin, 'Chip placed & cancelled!')
        self.betting(driver, betArea, game, placeConfirm=True)
        card_flipped(driver, game, tableDealer, results)
        self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
        self.wait_If_Clickable(driver, 'action', 'rebet')

        insufficient = self.customJS(driver, 'toast_check("Insufficient funds to rebet!");')
        message = self.debuggerMsg(tableDealer, 'Insufficient funds to rebet!')
        if insufficient:
            self.assertion(message, skip=True)
        else:
            cancelAssert(driver, game, tableDealer, allin, 'Rebet & Cancelled!')
            self.wait_If_Clickable(driver, 'action', 'rebet')
            self.customJS(driver, f'click(`{self.data("action", "confirm")}`);')
            self.screenshot(driver, 'Rebet & Confirmed!', tableDealer[0], allin)
            card_flipped(driver, game, tableDealer, results)

class PlayerUpdate(Utilities):

    def __init__(self) -> None:
        super().__init__()
        self.requests = Requests()

    def updateBalance(self, driver, game):
        """
        Update the user's balance, perform necessary balance adjustments, and navigate to the specified game lobby.

        params:
        `driver` (WebDriver): The Selenium WebDriver instance.
        `game` (str): The name or category of the game lobby to navigate to.

        : This function generates a random amount between $2000.00 and $10000.00 and converts it to a string
        : with two decimal places. It then adds this amount to the user's balance using the addBalance function
        : with the appropriate environment configurations for adding and deducting balance.
        : After updating the balance, the function navigates the WebDriver instance to the URL obtained from
        : getURL() and waits for the 'lobby' and 'main' elements to be available before proceeding.
        : It then waits for the specified game category to become clickable and retrieves a list of WebElement
        : objects representing the game tables available in the lobby.
        """

        amount = round(random.uniform(2000.00, 10000.00), 2)
        amount_str = f'{amount:.2f}'
        getBalance = self.requests.addBalance(self.env('add'), amount_str)
        self.requests.addBalance(self.env('deduc'), amount=getBalance)
        self.requests.addBalance(self.env('add'), amount)
        driver.get(self.requests.getURL())
        self.waitElement(driver, 'lobby', 'main')
        self.wait_If_Clickable(driver, 'category', game)
        elements = self.findElements(driver, 'lobby', 'table panel')
        return elements

    def checkPlayerBalance(self, driver, game, value="", lobbyBalance=False):
        """
        check the player's balance in the specified game lobby or during gameplay.

        params:
        `driver` (webdriver): the selenium webdriver instance.
        `game` (str): the name of the game or game category.
        `value` (str, optional): the expected balance value. default is an empty string.
        `lobbybal` (bool, optional): whether to check the balance in the lobby. default is false.

        : if the game is not 'roulette', it extracts the table and dealer information using the `table_dealer` function,
        : and locates the player's balance and game balance elements using the `findelement` function.
        : if `lobbybal` is true, it compares the lobby balance (`coins.text`) with the expected value.
        : otherwise, it compares the top balance (`coins.text`) with the bottom balance (`playerbalance.text`).
        """

        if game != 'roulette':
            tableDealer = self.table_dealer(driver)
            coins = self.findElement(driver, 'in-game', 'balance')
            playerBalance = self.findElement(driver, 'in-game', 'playerBalance')

            if lobbyBalance:
                message = self.debuggerMsg(tableDealer, f'Lobby {value} & '\
                f'In-game Balance {coins.text} - Expected: EQUAL')
                self.assertion(message, value, '==', coins.text.strip())

            message = self.debuggerMsg(tableDealer, f'Top {coins.text} & '\
            f'Bottom balance {playerBalance.text} - Expected: EQUAL')
            self.assertion(message, coins.text, '==', playerBalance.text)

class BetAllin(Betting):

    def __init__(self) -> None:
        super().__init__()

    def gameplay(self, driver, game, results, allin=False):
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

        bet_areas = list(self.data(game))
        tableDealer = self.table_dealer(driver)
        self.cancelRebet(driver, bet_areas, tableDealer, game, results, allin)
        self.minBet(driver, game, tableDealer, allin)
        self.editChips(driver)

        while True:
            coins = self.findElement(driver, 'in-game','balance')
            index = random.choice(range(len(bet_areas)))
            bets = self.dtSidebet(driver, game, index, bettingArea=bet_areas)
            try:
                self.customJS(driver, f'click(`{bets}`);')
            except ElementClickInterceptedException:
                self.waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
                self.customJS(driver, f'click(`{bets}`);')

            insufficient = self.customJS(driver, 'toast_check("Insufficient Balance");')

            if insufficient:
                self.screenshot(driver, 'Insufficient Balance', tableDealer[0], allin)
                self.customJS(driver, f'click(`{self.data("action", "confirm")}`);')
                self.waitElementInvis(driver, 'in-game', 'toast')

                if game == 'bull bull':
                    equalBet = []
                    coins = self.findElement(driver, 'in-game','balance')
                    for bet in bet_areas:
                        if 'EQUAL' in bet:
                            equalBet.append(bet)

                    randomSelect = random.choice(range(len(equalBet)))
                    if coins.text != '0.00':
                        self.customJS(driver, f'click("{self.data(game, equalBet[randomSelect])}");')
                        self.customJS(driver, f'click("{self.data("action", "confirm")}");')
                        self.waitElement(driver, 'in-game','toast')
                        self.waitElementInvis(driver, 'in-game','toast')
                else:
                    self.waitPresence(driver, 'in-game', 'balance', text='0.00', setTimeout=10)
                break

        message = self.debuggerMsg(tableDealer, f'All-in bet {coins.text} - Expected: 0.00')
        self.assertion(message, coins.text, '==', '0.00')
        self.sumBetPlaced(driver, game, tableDealer)

class BetPool(Utilities):

    def __init__(self) -> None:
        super().__init__()

    def payrates_odds(self, driver, game, tableDealer, allin=False):
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
            betLimit = self.data('bet-limit').get(game)
            for _, item in betLimit.items():
                odds.append(item)

            self.wait_If_Clickable(driver, 'in-game', 'payrate-modal')
            self.waitElement(driver, 'in-game', 'modal-bet')
            self.screenshot(driver, 'BET Limit - Payrate', tableDealer[0], allin)
            payrates = self.findElements(driver, 'in-game', 'payrates')
            sedie_payrates = self.findElements(driver, 'in-game', 'sedie-payrate')
            super6 = self.findElements(driver, 'super6', 's6')

            for payrate in payrates:
                game_odds.append(payrate.text)

            if game == 'baccarat' and len(super6) == 1:
                odds.append('(1:12)')
                odds[1] = '(1:1)'

            elif game == 'sedie':
                for payrate in sedie_payrates:
                    game_odds.append(payrate.text)

            elif game == 'dragontiger':
                tableNumbers = self.env('newDT').split(':')
                if tableDealer[0] in tableNumbers:
                    odds[2] = '(1:8)'

            message = self.debuggerMsg(tableDealer, f'Bet limit rate & Local bet limit rate - Expected: EQUAL')
            self.assertion(message, odds, '==', game_odds)

        else:
            self.wait_If_Clickable(driver, 'in-game', 'payrate-modal')
            self.waitElement(driver, 'in-game', 'modal-bet')
            self.screenshot(driver, 'BET Limit - MinMax', tableDealer[0], allin)

        minMaxLimit = self.findElements(driver, 'in-game', 'min-max')
        value = []
        for limit in minMaxLimit:
            if len(limit.text) != 0 or limit.text is not None or limit.text != '':
                value.append(True)
            else:
                value.append(False)

        message = self.debuggerMsg(tableDealer, f'Bet limit min-max are all displayed')
        self.assertion(message, all(value))
        self.wait_If_Clickable(driver, 'in-game', 'payrate-close')

class History(Utilities):

    def __init__(self) -> None:
        super().__init__()
        self.decoder = Decoder()

    def betHistory(self, driver, game, status, cardResults, extracted):
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
            blueCards = self.findElements(driver, 'history', selector)
            redCards = self.findElements(driver, 'history', 'result-red')
            atrribute = 'class' if game != 'bull bull' else 'style'
            self.decoder.getBaseImage(blueCards, atrribute, blue_card_value)
            self.decoder.getBaseImage(redCards, 'class', red_card_value)
            flippedCards = cardResults + len(blue_card_value + red_card_value)
            #remove empty strings
            newItems, newItems2, newDecode = [[],[],[]]

            #repeated loop to get cards base64 sequence same as the results
            for blue in blue_card_value:
                if blue.strip():
                    newItems.append(blue)

            for red in red_card_value:
                if red.strip():
                    newItems2.append(red)

            for item in newItems:
                if 'card-hidden' not in item:
                    newDecode.append(item)

            for item2 in newItems2:
                if 'card-hidden' not in item2:
                    newDecode.append(item2)

            card = self.decoder.decodeCropImage(newDecode, status)
            cardData = extracted + len(newItems + newItems2)
            self.deleteImages('screenshots\\decoded')

            return card, flippedCards, cardData

    def openBetHistory(self, driver, game, tableDealer, oldRow=0, updates=False):
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
            self.wait_If_Clickable(driver, 'history', 'button')
            self.waitElement(driver, 'history', 'modal')
            selectGame = self.data('history', 'filter')
            gameIndex = self.data('game list', game)
            self.customJS(driver, f'selectGameList("{selectGame}", {gameIndex})')
            expand = self.findElement(driver, 'history', 'expand', status=True)

            try:
                while expand.is_displayed():
                    self.wait_If_Clickable(driver, 'history', 'expand', setTimeout=3)
            except:
                ...

            self.waitElementInvis(driver, 'history', 'expand')
            countRows = self.findElements(driver, 'history', 'detail')
            if len(countRows) != 0 and updates:
                status = []
                flippedCards = 0
                extracted = 0
                rowsAdded = len(countRows) - oldRow
                message = self.debuggerMsg(tableDealer, f'Bet History {rowsAdded} new rows has been added')
                self.assertion(message, len(countRows), '>', oldRow, notice=True)
                dataTable = self.findElement(driver, 'history', 'data table')
                detail = self.findElements(driver, 'history', 'detail')
                tableStage = self.findElements(driver, 'history', 'table')
                driver.execute_script("arguments[0].scrollTop = 0;", dataTable)

                for rows in range(rowsAdded):
                    detail[rows].click()
                    getTable = tableStage[rows].text
                    self.waitElement(driver, 'history', 'result')
                    baseList, flippedCards, extracted = self.betHistory(driver, game, status, flippedCards, extracted)
                    #creates log history for debugging in case of failure
                    with open('logs\\logs.txt', 'a') as logs:
                        newLine = '\n'
                        logs.write(f'Index {rows} {getTable.replace(f"{newLine}"," ")} -'\
                        f'Cards {baseList} {newLine} ')

                    self.wait_If_Clickable(driver, 'history', 'close card')
                    self.waitElementInvis(driver, 'history', 'result')

                if len(status) != 0:
                    if all(status):
                        message = self.debuggerMsg(tableDealer, f'Decoded Cards {flippedCards} & '\
                        f'Extracted Values {extracted} - Expected - EQUAL ')
                        self.assertion(message, flippedCards, '==', extracted)
                    else:
                        message = self.debuggerMsg(tableDealer, 'One or more extracted card data '\
                        f'was not in the list of cards')
                        self.assertion(message, notice=True)
                else:
                    message = self.debuggerMsg(tableDealer, 'History results is empty!')
                    self.assertion(message, notice=True)

            self.wait_If_Clickable(driver, 'in-game', 'payrate-close')
            self.waitElementInvis(driver, 'history', 'modal')
            
            return len(countRows)

class Chat(Utilities):

    def __init__(self) -> None:
        super().__init__()

    def chat(self, driver, game, tableDealer):
        """
        send chat messages within the game interface and verify their display

        params:
        `driver` (webdriver): The Selenium WebDriver instance.
        `game` (str): The name of the game.
        `tableDealer` (str): a string containing information about the table and dealer.

        : Clicks on the chat button to open the chat interface.
        : Waits for the send button to appear in the chat interface.
        : Generates and sends chat messages using random text and emojis.
        : Verifies if the chat messages are displayed and not empty.
        : Checks if the length of each chat message does not exceed 22 characters.
        """

        if game not in ['sicbo', 'roulette']:
            self.wait_If_Clickable(driver, 'chat', 'button')
            self.waitPresence(driver, 'chat', 'send', text='Send', setTimeout=3)
            sendMessage = self.findElement(driver, 'chat', 'input')
            cn = Faker(['zh_TW'])
            getLength = []
            while True:
                sendMessage.send_keys(cn.text())
                self.wait_If_Clickable(driver, 'chat', 'send')
                for _ in range(10):
                    pyperclip.copy(fake.emoji())
                    action = ActionChains(driver)
                    action.key_down(Keys.CONTROL).send_keys("v")
                    action.key_up(Keys.CONTROL).perform()

                self.wait_If_Clickable(driver, 'chat', 'send')
                text = self.findElements(driver, 'chat', 'messages')
                sendMessage.send_keys(fake.text())
                self.wait_If_Clickable(driver, 'chat', 'send')
                message = self.debuggerMsg(tableDealer, 'Chatbox messages are displayed or not empty')
                self.assertion(message, len(text), '!=', 0, notice=True)
                for msg in text:
                    textCount = sum(1 for _ in grapheme.graphemes(msg.text.strip()))
                    if textCount <= 22:
                        getLength.append(True)
                    else:
                        getLength.append(False)
                        print(msg.text, len(msg.text))
                break

            message = self.debuggerMsg(tableDealer, 'Chat messages sent does not exceed 22 characters')
            self.assertion(message, all(getLength))
