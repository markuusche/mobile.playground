from src.libs.modules import *
from src.utilities.helpers import *
from src.request.api import *
from .. import GS_REPORT

# for digital message screenshots
def screenshot(driver, name, val, allin=False):
    if allin:
        driver.save_screenshot(f'screenshots/{name} {val}.png')

def debuggerMsg(tableDealer, str="", str2=""):
    return f'[Table: {tableDealer[0]} Dealer: {tableDealer[1]}] '\
        f'{str} {str2}'

# delete all screenshots and images
def deleteImages(folder, logs=False):
    path = f'{folder}\\'
    files = os.listdir(path)
    for file in files:
        pathFile = os.path.join(path, file)
        if os.path.isfile(pathFile):
            os.remove(pathFile)

    if logs:
        logpath = 'logs\\'
        txt = os.listdir(logpath)
        for log in txt:
            truePath = os.path.join(logpath, log)
            if os.path.exists(truePath):
                os.remove(truePath)

#close video stream to avoid lag
def disableStream(driver, stream):
    if not stream:
        toggled = findElement(driver, 'in-game', 'video-toggled')
        isToggled = toggled.get_attribute('class')
        while 'toggled' in isToggled:
            customJS(driver, f'click("{data("in-game", "close-video")}");')
            stream = True
            break

def skipOnFail(driver, tableDealer, exception):
    """
    Skip the current test case upon encountering an exception, refresh the driver, and clear the GS_REPORT.
    
    params:
    `driver` (webdriver): The Selenium WebDriver instance.
    `tableDealer` (string): A string containing information about the table and dealer.
    `exception` (exception: The exception raised during the test execution.

    : This function is designed to handle test case failures gracefully by logging the exception details and 
    : traceback information to a file. It then refreshes the WebDriver instance, clears any existing report data, 
    : and waits for the 'lobby' and 'main' elements to be available before proceeding.  
    : It extracts the exception message and traceback, appends them to a log file named 'tracelogs.txt' with 
    : information about the table and dealer, and separates each log entry with a newline for clarity.
    """
    
    message = debuggerMsg(tableDealer, f'---- SKIPPED ----')
    assertion(message, notice=True)
    driver.refresh()
    waitElement(driver, 'lobby', 'main')
    print('=' * 100)
    GS_REPORT.clear()
    
    exc = str(exception).split('Stacktrace:')[0].strip()
    tb = traceback.format_exc().split('Stacktrace:')[0].strip()

    with open('logs\\tracelogs.txt','a') as logs:
        logs.write(f'Table: {tableDealer[0]} Dealer: {tableDealer[1]} \n {exc} \n'\
        f'\nTraceback: {tb} \n\n')

def updateBalance(driver, game):
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
    getBalance = addBalance(env('add'), amount_str)
    addBalance(env('deduc'), amount=getBalance)
    addBalance(env('add'), amount)
    driver.get(getURL())    
    waitElement(driver, 'lobby', 'main')
    wait_If_Clickable(driver, 'category', game)
    elements = findElements(driver, 'lobby', 'table panel')
    return elements

def checkPlayerBalance(driver, game, value="", lobbyBalance=False):
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
        tableDealer = table_dealer(driver)
        coins = findElement(driver, 'in-game', 'balance')
        playerBalance = findElement(driver, 'in-game', 'playerBalance')
        
        if lobbyBalance:
            message = debuggerMsg(tableDealer, f'Lobby Balance {value} & '\
            f'In-game Balance {coins.text} - Expected: EQUAL')
            assertion(message, value, '==', coins.text.strip())

        message = debuggerMsg(tableDealer, f'Top balance {coins.text} & '\
        f'Bottom balance {playerBalance.text} - Expected: EQUAL')
        assertion(message, coins.text, '==', playerBalance.text)

def LoseOrWin(driver):
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
    
    waitElement(driver, 'in-game', 'resultToast')
    result = findElement(driver, 'in-game', 'winloss')
    if '-' in result.text:
        getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
        return f'Lose: {getText:.2f}'
    else:
        getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
        return f'Win: {getText:.2f}'

def dtSidebet(driver, game, getIndex, bettingArea=None, minBet=False):
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
        shoe = findElement(driver, 'in-game', 'shoe')
        tableRound = int(shoe.text.split('-')[1])
        if tableRound <= 30:
            sidebet = data(game)
            sidebet.update(data('sidebet', 'dragontiger'))
            bet_areas = list(sidebet)
            index = random.choice(range(len(bet_areas)))
            return sidebet[bet_areas[index]]
        else:
            return data(game, bettingArea[getIndex])
    else:
        index = random.choice(range(len(bettingArea)))
        return data(game, bettingArea[index])

def minBet(driver, game, tableDealer, allin=False):
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
    
    if game != 'roulette' or game != 'sicbo':
        def getElementText(selector):
            return selector.text
        
        def popItem(listItem: list[int]):
            index = listItem
            index.reverse()
            for item in index:
                minimumBets.pop(item)
                betNames.pop(item)

        wait_If_Clickable(driver, 'in-game', 'payrate-modal')
        screenshot(driver, 'Minimum Bets', tableDealer[0], allin)
        waitElement(driver, 'in-game', 'modal-bet')
        
        if game == 'sedie':
            customJS(driver , 'sedieBeads();')
            
        minmax = findElements(driver, 'in-game', 'min-max')
        betLabel = findElements(driver, 'in-game', 'limit label')

        minimumBets = []
        betNames = []
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
            shoe = findElement(driver, 'in-game', 'shoe')
            tableRound = int(shoe.text.split('-')[1])
            if tableRound <= 30:
                index = [3,4,7,8]
            else:
                index = [3,4,5,6,7,8,9,10]
                
            popItem(index)
        
        newData = {}
        for key, value in zip(minimumBets, betNames):
            newData[value] = key
        
        wait_If_Clickable(driver, 'in-game', 'payrate-close')
        waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
        
        #start betting minimum bets
        assertMin = []
        bets = list(newData)
        for bet in range(len(bets)):
            sidebet = data(game)
            amount = int(newData[bets[bet]]) - 1
            editChips(driver, add=True, amount=amount)
            timer = findElement(driver, 'in-game', 'timer')
            try:
                if int(timer.text) <= 3:
                    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            except:
                waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

            if game == 'baccarat' and 'S6' in bets:
                sidebet['S6'] = data('super6', 's6')
                betS6 = list(sidebet)
                betAction = sidebet[f'{betS6[bet]}']
            elif game == 'dragontiger':
                if len(bets) > 3:
                    sidebet.update(data('sidebet', 'dragontiger'))
                    newBetArea = list(sidebet)
                    betAction = sidebet[f'{newBetArea[bet]}']
                else:
                    betAction = data(game, bets[bet])
            else:
                betAction = data(game, bets[bet])
            
            customJS(driver, f'click("{betAction}");')
            customJS(driver, f'click("{data("action", "confirm")}");')
            status = waitPresence(driver, 'in-game', 'toast', text='Below Minimum Limit', setTimeout=1.2)
            if status:
                assertMin.append(True)
            else:
                screenshot(driver, 'Minimum bet failed', tableDealer[0], allin)
                print(f'[{tableDealer[0]}] Locator: {betAction}')
                assertMin.append(False)
        
        message = debuggerMsg(tableDealer, 'Minimum Bet Betting')
        assertion(message, all(assertMin))
        if game == 'bull bull':
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')

def betting(driver, betArea, game, placeConfirm=False):
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
    
    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
    loopRange = 10 if game in ['sicbo', 'roulette'] else len(betArea)
    s6 = random.choice(range(2))
    if placeConfirm:
        if s6 == 1 and game == 'baccarat':
            wait_If_Clickable(driver, 'super6', 'r-area')
            waitElement(driver, 'super6', 's6')
            wait_If_Clickable(driver, 'super6', 's6')

    i = 0
    while i < loopRange:
        index = random.choice(range(len(betArea)))
        bets = dtSidebet(driver, game, index, bettingArea=betArea)
        try:
            customJS(driver, f'click("{bets}");')
            if placeConfirm:
                wait_If_Clickable(driver, 'action', 'confirm')

            i += 1
        except ElementClickInterceptedException:
            break

def getChipValue(driver):
    """
    calculate the total amount of chips placed on the game table.
    
    params:
    `driver` (webdriver): the selenium webdriver instance.
    
    : find all elements representing the total amount of money placed on the game table using `findelements`.
    : loop through each element to extract the chip amount, remove any comma separators, 
    : and convert it to a float. add up all the chip amounts to get the total.
    
    returns:
    :`float` the total amount of chips placed on the game table.
    """
    
    chips = 0.00
    placed_chips = findElements(driver, 'in-game', 'totalMoney')

    for chip in placed_chips:
        if chip.text != '':
            chips += float(chip.text.replace(',',''))
    
    return chips

def cancelRebet(driver, betArea, tableDealer, game, allin=False):
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
        wait_If_Clickable(driver, 'action', 'cancel')
        screenshot(driver, texts, tableDealer[0], allin)
        sumBetPlaced(driver, game, tableDealer, cancel=True, text=texts)
    
    def card_flipped(driver, game, tableDealer):
        if game in ['baccarat', 'dragontiger', 'three-cards', 'bull bull']:
            waitPresence(driver, 'in-game','toast', text='No More Bets!')
            waitElementInvis(driver, 'in-game', 'toast')
            waitElement(driver, 'in-game', 'toast')
            cardFlips(driver, tableDealer)
    
    betting(driver, betArea, game)
    chips = getChipValue(driver)
    message = debuggerMsg(tableDealer, '\033[93mChips are being placed.') 
    assertion(message, chips, '>', 0, notice=True)

    cancelAssert(driver, game, tableDealer, allin, 'Chip placed & cancelled!')
    betting(driver, betArea, game, placeConfirm=True)
    card_flipped(driver, game, tableDealer)
    waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
    wait_If_Clickable(driver, 'action', 'rebet')

    insufficient = customJS(driver, 'toast_check("Insufficient funds to rebet!");')
    message = debuggerMsg(tableDealer, 'Insufficient funds to rebet!')
    if insufficient:
        assertion(message, skip=True)
    else:
        cancelAssert(driver, game, tableDealer, allin, 'Rebet & Cancelled!')
        wait_If_Clickable(driver, 'action', 'rebet')
        wait_If_Clickable(driver, 'action', 'confirm')
        screenshot(driver, 'Rebet & Confirmed!', tableDealer[0], allin)
        card_flipped(driver, game, tableDealer)

def editChips(driver, divideBy=10, add=False, amount=0):
    """
    edit the chip amount in the game interface and return the updated chip value.
    
    params:
    `driver` (webdriver): the selenium webdriver instance.
    `divideby` (int, optional): the divisor used to calculate the new chip amount. default is 10.
    
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
    
    bets = findElement(driver, 'in-game', 'balance')
    value = float(bets.text.replace(',',''))
    if add:
        chips = amount
    else:
        chips = int(value) / divideBy
    wait_If_Clickable(driver, 'in-game', 'edit')
    waitElement(driver, 'in-game', 'chip amount')
    wait_If_Clickable(driver, 'in-game', 'edit button')
    wait_If_Clickable(driver, 'in-game', 'clear')
    input = findElement(driver, 'in-game', 'input chips')
    input.send_keys(int(chips))
    wait_If_Clickable(driver, 'in-game', 'save amount')
    wait_If_Clickable(driver, 'in-game', 'payrate-close')
    waitElementInvis(driver, 'in-game', 'chip amount')

def gameplay(driver, game, allin=False):
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
    
    bet_areas = list(data(game))
    tableDealer = table_dealer(driver)
    cancelRebet(driver, bet_areas, tableDealer, game, allin)
    minBet(driver, game, tableDealer, allin)
    editChips(driver)

    while True:
        coins = findElement(driver, 'in-game','balance')
        index = random.choice(range(len(bet_areas)))
        bets = dtSidebet(driver, game, index, bettingArea=bet_areas)
        try:
            customJS(driver, f'click("{bets}");')
        except ElementClickInterceptedException:
            waitPresence(driver, 'in-game', 'toast', text='Please Place Your Bet!')
            customJS(driver, f'click("{bets}");')

        insufficient = customJS(driver, 'toast_check("Insufficient Balance");')

        if insufficient:
            screenshot(driver, 'Insufficient Balance', tableDealer[0], allin)
            wait_If_Clickable(driver, 'action', 'confirm')
            waitElementInvis(driver, 'in-game','toast')
            
            if game == 'bull bull':
                equalBet = []
                coins = findElement(driver, 'in-game','balance')
                for bet in bet_areas:
                    if 'EQUAL' in bet:
                        equalBet.append(bet)
                        
                randomSelect = random.choice(range(len(equalBet)))
                if coins.text != '0.00':
                    customJS(driver, f'click("{data(game, equalBet[randomSelect])}");')
                    customJS(driver, f'click("{data("action", "confirm")}");')
                    waitElement(driver, 'in-game','toast')
                    waitElementInvis(driver, 'in-game','toast')
            else:
                waitPresence(driver, 'in-game', 'balance', text='0.00', setTimeout=10)
            break
        
    message = debuggerMsg(tableDealer, f'All-in bet {coins.text} - Expected: 0.00')
    assertion(message, coins.text, '==', '0.00')
    sumBetPlaced(driver, game, tableDealer)

def payrates_odds(driver, game, tableDealer, allin=False):
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
        odds = []
        game_odds = []
        betLimit = data('bet-limit').get(game)
        for _, item in betLimit.items():
            odds.append(item)

        wait_If_Clickable(driver, 'in-game', 'payrate-modal')
        waitElement(driver, 'in-game', 'modal-bet')
        screenshot(driver, 'BET Limit - Payrate', tableDealer[0], allin)
        payrates = findElements(driver, 'in-game', 'payrates')
        sedie_payrates = findElements(driver, 'in-game', 'sedie-payrate')
        super6 = findElements(driver, 'super6', 's6')

        for payrate in payrates:
            game_odds.append(payrate.text)

        if game == 'baccarat' and len(super6) == 1:
            odds.append('(1:12)')
            odds[1] = '(1:1)'

        elif game == 'sedie':
            for payrate in sedie_payrates:
                game_odds.append(payrate.text)

        elif game == 'dragontiger':
            tableNumbers = env('newDT').split(':')
            if tableDealer[0] in tableNumbers:
                odds[2] = '(1:8)'

        message = debuggerMsg(tableDealer, f'Bet limit rate & Local bet limit rate - Expected: EQUAL')
        assertion(message, odds, '==', game_odds)

    else:
        wait_If_Clickable(driver, 'in-game', 'payrate-modal')
        waitElement(driver, 'in-game', 'modal-bet')
        screenshot(driver, 'BET Limit - MinMax', tableDealer[0], allin)

    minMaxLimit = findElements(driver, 'in-game', 'min-max')
    value = []
    for limit in minMaxLimit:
        if len(limit.text) != 0 or limit.text is not None or limit.text != '':
            value.append(True)
        else:
            value.append(False)

    message = debuggerMsg(tableDealer, f'Bet limit min-max are not all displayed')
    assertion(message, all(value))
    wait_If_Clickable(driver, 'in-game', 'payrate-close')

def sumBetPlaced(driver, game, tableDealer, cancel=False, text=None):
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

    chips = getChipValue(driver)
    total = 0.00

    if cancel:
        message = debuggerMsg(tableDealer, f'{text} {chips} - Expected: No chips placed')
        assertion(message, chips, '==', 0)
    else:
        if game != 'bull bull':
            bets = findElement(driver, 'in-game', 'bets')
            if bets != None:
                total = float(bets.text.replace(',',''))
                message = debuggerMsg(tableDealer, f'Placed chips {round(chips, 2)} '\
                f'& Bets {total} - Expected: EQUAL')
                assertion(message, round(chips, 2), '==', total)
            else:
                message = debuggerMsg(tableDealer, f'\033[91m"Bets:" is empty, cannot confirm and '\
                f'compare chips value with the placed chips\033[0m')
                assertion(message, skip=True)

def verifiy_newRound(driver, bet, tableDealer):
    """
    verify the absence of new round digital results and the status of placed chips

    params:
    `driver` (webdriver): the selenium webdriver instance.
    `bet` (str): the name of the game.
    `tableDealer` (str): A string containing information about the table and dealer.

    : defines a nested function `verify_digitalresult` to check if digital results are displayed for a new round.
    : determines the game type and verifies digital results accordingly.
    : if the game type is 'baccarat', 'three-cards', 'dragontiger', or 'bull bull', checks for the absence of digital results.
    : for 'sicbo' and 'roulette' games, verifies the absence of digital results.
    : checks the status of placed chips after the new round and ensures that no chips are placed.

    """
    
    def verify_digitalResult(driver, game, tableDealer):
        digital = findElement(driver, 'digital results', game)
        message = debuggerMsg(tableDealer, 'New Round Digital Result not displayed!')
        assertion(message, digital.is_displayed(), '==', False)
    
    if bet in ['baccarat', 'three-cards', 'dragontiger', 'bull bull']:
        verify_digitalResult(driver, 'bdt', tableDealer)
    elif bet == 'sicbo':
        verify_digitalResult(driver, 'sicbo', tableDealer)
    elif bet == 'roulette':
        verify_digitalResult(driver, 'roulette', tableDealer)
    else:
        waitElementInvis(driver, 'digital results', 'sedie', \
        setTimeout=3, isDigital=True, tableDealer=tableDealer)
    
    sumBetPlaced(driver, bet, tableDealer, cancel=True, text='No placed chips after new round')
 
def summary(driver, game, tableDealer):
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
                summaries = findElements(driver, 'in-game', 'summary')
                
            if game == 'sedie':
                summaries = findElements(driver, 'in-game', 'sedie-summary')
                sideBtn = findElements(driver, 'in-game', 'sedie-sidebtn')
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
            
            shoe = findElement(driver, 'in-game', 'shoe')
            if game in ['three-cards', 'sedie']:
                value = int(shoe.text)
            else:
                value = int(shoe.text.split('-')[1])
                
            message = debuggerMsg(tableDealer, f'Rodmap total summary {total}, '\
            f'Shoe round {value} - Expected: round > total')
            assertion(message, total, '==', value -1)

def check_raceTracker(driver, tableDealer):
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

    findElement(driver, 'in-game', 'switch', click=True)
    waitElement(driver, 'in-game', 'race-tracker', setTimeout=3)
    raceTracker = findElement(driver, 'in-game', 'race-tracker')
    message = debuggerMsg(tableDealer, 'Race Tracker is displayed.')
    assertion(message, raceTracker.is_displayed(), '==', True)
    findElement(driver, 'in-game', 'switch', click=True)

def table_dealer(driver):
    """
    retrieve the table number and dealer information.

    params:
    `driver` (webdriver): the selenium webdriver instance.

    find and return the table number and dealer's name.
    """
    tableNumber = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game', 'dealer')
    return tableNumber.text, dealer.text

def getBaseImage(cards, attribute, cardList):
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

def decodeCropImage(decoded, status):
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
        if str(value.replace('\n','')) in str(data('cards')):
            status.append(True)
            card.append(str(value.replace('\n','')))
        else:
            print(str(value.replace('\n',''), 'card value that is not in data("cards")'))
            status.append(False)

    return card

def betHistory(driver, game, status, cardResults, extracted):
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
        blue_card_value = []
        red_card_value = []
        selector = 'result-blue' if game != 'bull bull' else 'result-blue-bull'
        blueCards = findElements(driver, 'history', selector)
        redCards = findElements(driver, 'history', 'result-red')
        atrribute = 'class' if game != 'bull bull' else 'style'
        getBaseImage(blueCards, atrribute, blue_card_value)
        getBaseImage(redCards, 'class', red_card_value)
        flippedCards = cardResults + len(blue_card_value + red_card_value)
        #remove empty strings
        newItems = []
        newItems2 = []
        
        #repeated loop to get cards base64 sequence same as the results
        for blue in blue_card_value:
            if blue.strip():
                newItems.append(blue)

        for red in red_card_value:
            if red.strip():
                newItems2.append(red)
        
        newDecode = []
        for item in newItems:
            if 'card-hidden' not in item:
                newDecode.append(item)
        
        for item2 in newItems2:
            if 'card-hidden' not in item2:
                newDecode.append(item2)
        
        card = decodeCropImage(newDecode, status)
        cardData = extracted + len(newItems + newItems2)
        deleteImages('screenshots\\decoded')

        return card, flippedCards, cardData

def cardFlips(driver, tableDealer):
    waitElementInvis(driver, 'in-game', 'toast')
    newDecode = []
    blue = findElements(driver, 'in-game', 'result-card-blue')
    red = findElements(driver, 'in-game', 'result-card-red')
    getBaseImage(blue, 'style', newDecode)
    getBaseImage(red, 'style', newDecode)
    
    status = []
    decodeCropImage(newDecode, status)
    message = debuggerMsg(tableDealer, '\033[93mResult cards are flipped')
    assertion(message, all(status), notice=True)
    
def openBetHistory(driver, game, tableDealer, oldRow=0, updates=False):
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
        wait_If_Clickable(driver, 'history', 'button')
        waitElement(driver, 'history', 'modal')
        expand = findElement(driver, 'history', 'expand', status=True)
        selectGame = data('history', 'filter')
        gameIndex = data('game list', game)
        customJS(driver, f'selectGameList("{selectGame}", {gameIndex})')

        try:
            while expand.is_displayed():
                wait_If_Clickable(driver, 'history', 'expand', setTimeout=3)
        except:
            ...

        row = findElement(driver, 'history', 'transactions')
        parseRow = int(row.text.replace(',',''))
        if parseRow != 0:
            if updates:
                status = []
                flippedCards = 0
                extracted = 0
                rowsAdded = parseRow - oldRow
                message = debuggerMsg(tableDealer, f'Bet History {rowsAdded} new rows has been added')
                assertion(message, parseRow, '>', oldRow, notice=True)
                dataTable = findElement(driver, 'history', 'data table')
                detail = findElements(driver, 'history', 'detail')
                tableStage = findElements(driver, 'history', 'table')
                driver.execute_script("arguments[0].scrollTop = 0;", dataTable)

                for rows in range(rowsAdded):
                    detail[rows].click()
                    getTable = tableStage[rows].text
                    waitElement(driver, 'history', 'result')
                    baseList, flippedCards, extracted = betHistory(driver, game, status, flippedCards, extracted)
                    #creates log history for debugging in case of failure
                    with open('logs\\logs.txt', 'a') as logs:
                        newLine = '\n'
                        logs.write(f'Index {rows} {getTable.replace(f"{newLine}"," ")} -'\
                        f'Cards {baseList} {newLine} ')

                    wait_If_Clickable(driver, 'history', 'close card')
                    waitElementInvis(driver, 'history', 'result')

                if len(status) != 0:
                    if all(status):
                        message = debuggerMsg(tableDealer, f'Decoded base64 Image {flippedCards} & '\
                        f'Extracted Card Value {extracted} - Expected - EQUAL ')
                        assertion(message, flippedCards, '==', extracted)
                    else:
                        message = debuggerMsg(tableDealer, 'One or more extracted card data '\
                        f'was not in the list of cards')
                        assertion(message, notice=True)
                else:
                    message = debuggerMsg(tableDealer, 'History results is empty!')
                    assertion(message, notice=True)

        wait_If_Clickable(driver, 'in-game', 'payrate-close')
        waitElementInvis(driver, 'history', 'modal')

        return parseRow

def chat(driver, game, tableDealer):
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
        wait_If_Clickable(driver, 'chat', 'button')
        waitPresence(driver, 'chat', 'send', text='Send', setTimeout=3)
        sendMessage = findElement(driver, 'chat', 'input')
        cn = Faker(['zh_TW'])
        getLength = []
        while True:
            sendMessage.send_keys(cn.text())
            wait_If_Clickable(driver, 'chat', 'send')
            for _ in range(10):
                pyperclip.copy(fake.emoji())
                action = ActionChains(driver)
                action.key_down(Keys.CONTROL).send_keys("v")
                action.key_up(Keys.CONTROL).perform()

            wait_If_Clickable(driver, 'chat', 'send')
            text = findElements(driver, 'chat', 'messages')
            sendMessage.send_keys(fake.text())
            wait_If_Clickable(driver, 'chat', 'send')
            message = debuggerMsg(tableDealer, 'Chatbox messages are displayed or not empty')
            assertion(message, len(text), '!=', 0, notice=True)
            for msg in text:
                textCount = sum(1 for _ in grapheme.graphemes(msg.text.strip()))
                if textCount <= 22:
                    getLength.append(True)
                else:
                    getLength.append(False)
                    print(msg.text, len(msg.text))
            break

        message = debuggerMsg(tableDealer, 'Chat messages sent does not exceed 22 characters')
        assertion(message, all(getLength))
    
# soft assertion function
def assertion(message, comparison=None, operator=None, comparison2=None, skip=False, notice=False):
    red = '\033[91m'
    green = '\033[32m'
    default = '\033[0m'
    yellow = '\033[93m'
    
    if notice:
        status = 'NOTICE'
        color = yellow
    else:
        status = 'PASSED'
        color = green
    
    if skip:
        print(f'{yellow}SKIPPED{default} {message}')
        GS_REPORT.append(['SKIPPED'])
    else:
        try:
            if operator == '==':
                assert comparison == comparison2
            elif operator == '!=':
                assert comparison != comparison2
            elif operator == '>':
                assert comparison > comparison2
            elif operator == '<':
                assert comparison < comparison2
            elif operator == 'in':
                assert comparison in comparison2
            else:
                assert comparison
            
            print(f'{color}{status}{default} {message}')
            if not notice:
                GS_REPORT.append(['PASSED'])
        except AssertionError:
            print(f'{red}FAILED{default} {message}')
            if not notice:
                GS_REPORT.append(['FAILED'])
