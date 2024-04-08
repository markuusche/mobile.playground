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

#skip a failed table, get logs and proceed to next iteration
def skipOnFail(driver, tableDealer, exception):
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

# reset coins to default amount when betting all-in. 
# for every table loop
def reset_coins(driver, game):
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

# check if the player balance from top left panel icon
# and in the middle panel matches.
def checkPlayerBalance(driver, game, value="", allin=False, lobbyBal=False):
    if game != 'roulette':
        tableDealer = table_dealer(driver)
        coins = findElement(driver, 'in-game', 'balance')
        playerBalance = findElement(driver, 'in-game', 'playerBalance')
        
        if lobbyBal:
            message = debuggerMsg(tableDealer, f'Lobby Balance {value} & '\
            f'In-game Balance {coins.text} - Expected: EQUAL')
            assertion(message, value, '==', coins.text.strip())

        message = debuggerMsg(tableDealer, f'Top balance {coins.text} & '\
        f'Bottom balance {playerBalance.text} - Expected: EQUAL')
        assertion(message, coins.text, '==', playerBalance.text)

# gets Lose or Win message with the values
def LoseOrWin(driver):
    waitElement(driver, 'in-game', 'resultToast')
    result = findElement(driver, 'in-game', 'winloss')
    if '-' in result.text:
        getText = float(result.text.replace('W/L', '').replace('-','').replace(' ','').replace(':',''))
        return f'Lose: {getText:.2f}'
    else:
        getText = float(result.text.replace('W/L', '').replace('+','').replace(' ','').replace(':',''))
        return f'Win: {getText:.2f}'

def dtSidebet(driver, game, betArea=None):
    shoe = findElement(driver, 'in-game', 'shoe')
    tableRound = int(shoe.text.split('-')[1])
    
    #side bet betting
    if game == 'dragontiger' and tableRound <= 30:
        sidebet = data(game)
        sidebet.update(data('sidebet', 'dragontiger'))
        bet_areas = list(sidebet)
        index = random.choice(range(len(bet_areas)))
        return sidebet[bet_areas[index]]
    else:
        index = random.choice(range(len(betArea)))
        return data(game, betArea[index])

def betting(driver, betArea, game, placeConfirm=False):
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
        bets = dtSidebet(driver, game, betArea=betArea)
        try:
            customJS(driver, f'click("{bets}");')
            if placeConfirm:
                wait_If_Clickable(driver, 'action', 'confirm')

            i += 1
        except ElementClickInterceptedException:
            break

def getChipValue(driver):
    chips = 0.00
    placed_chips = findElements(driver, 'in-game', 'totalMoney')

    for i in placed_chips:
        if i.text != '':
            chips += float(i.text.replace(',',''))
    
    return chips

# cancel and then rebet test case
def cancelRebet(driver, betArea, tableDealer, game, allin=False):
    #cancel function
    def cancelAssert(driver, game, tableDealer, allin, texts):
        wait_If_Clickable(driver, 'action', 'cancel')
        screenshot(driver, texts, tableDealer[0], allin)
        sumBetPlaced(driver, game, tableDealer, cancel=True, text=texts)
        
    betting(driver, betArea, game)
    chips = getChipValue(driver)
    message = debuggerMsg(tableDealer, '\033[93mChips are being placed.') 
    assertion(message, chips, '>', 0, notice=True)

    cancelAssert(driver, game, tableDealer, allin, 'Chip placed & cancelled!')
    betting(driver, betArea, game, placeConfirm=True)
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

# edit chips from in-game
def editChips(driver, divideBy=10):
    bets = findElement(driver, 'in-game', 'balance')
    value = float(bets.text.replace(',',''))
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
    return chips

# Bet all coins until Insufficient funds message appear
def coins_allin(driver, game, allin=False):
    bet_areas = list(data(game))
    tableDealer = table_dealer(driver)
    cancelRebet(driver, bet_areas, tableDealer, game, allin)
    editChips(driver)

    while True:
        coins = findElement(driver, 'in-game','balance')
        bets = dtSidebet(driver, game, betArea=bet_areas)
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
                    if 'Equal' in bet:
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

# verifies payrates matches with the payrate
# from yaml file
def payrates_odds(driver, game, tableDealer, allin=False):
    if game != 'bull bull':
        defaultPay = []
        list_pays = []
        betLimit = data('bet-limit').get(game)
        for _, x in betLimit.items():
            defaultPay.append(x)

        wait_If_Clickable(driver, 'in-game', 'payrate-modal')
        waitElement(driver, 'in-game', 'modal-bet')
        screenshot(driver, 'BET Limit - Payrate', tableDealer[0], allin)
        payrates = findElements(driver, 'in-game', 'payrates')
        sedie_payrates = findElements(driver, 'in-game', 'sedie-payrate')
        s6 = findElements(driver, 'super6', 's6')

        for payrate in payrates:
            list_pays.append(payrate.text)

        if game == 'baccarat' and len(s6) == 1:
            defaultPay.append('(1:12)')
            defaultPay[1] = '(1:1)'

        if game == 'sedie':
            for payrate in sedie_payrates:
                list_pays.append(payrate.text)

        if game == 'dragontiger':
            getDT = env('newDT')
            listDT = getDT.split(':')

            if tableDealer[0] in listDT:
                defaultPay[2] = '(1:8)'

        message = debuggerMsg(tableDealer, f'Bet limit rate & Local bet limit rate - Expected: EQUAL')
        assertion(message, defaultPay, '==', list_pays)

    else:
        wait_If_Clickable(driver, 'in-game', 'payrate-modal')
        waitElement(driver, 'in-game', 'modal-bet')
        screenshot(driver, 'BET Limit - MinMax', tableDealer[0], allin)

    minMax = findElements(driver, 'in-game', 'min-max')
    value = []
    for i in minMax:
        if len(i.text) != 0 or i.text is not None or i.text != '':
            value.append(True)
        else:
            value.append(False)

    message = debuggerMsg(tableDealer, f'Bet limit min-max are not all displayed')
    assertion(message, all(value), '==', True)
    wait_If_Clickable(driver, 'in-game', 'payrate-close')

# get the total placed chip value
# and compare it to Bets from betting area
def sumBetPlaced(driver, game, tableDealer, cancel=False, text=None):
        chips = getChipValue(driver)
        total = 0.00

        # check if bet area has 0 chips
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

# new round verification test case
def verifiy_newRound(driver, bet, tableDealer):
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

def verify_digitalResult(driver, game, tableDealer):
    digital = findElement(driver, 'digital results', game)
    message = debuggerMsg(tableDealer, 'New Round Digital Result is displayed!')
    assertion(message, digital.is_displayed(), '==', False)
 
# verifies in-game roadmap summary visibility and assertion    
def summary(driver, game, tableDealer):
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
            
            for j, i in enumerate(summaries):
                if game == 'three-cards' and j == 3:
                    continue
                if game == 'sedie' and j != 2 and j != 3:
                    continue
                
                match = re.search(r'\d+', i.text)
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

# check race tracker visibility
def check_raceTracker(driver, tableDealer):
    findElement(driver, 'in-game', 'switch', click=True)
    waitElement(driver, 'in-game', 'race-tracker', setTimeout=3)
    raceTracker = findElement(driver, 'in-game', 'race-tracker')
    message = debuggerMsg(tableDealer, 'Race Tracker is displayed.')
    assertion(message, raceTracker.is_displayed(), '==', True)
    findElement(driver, 'in-game', 'switch', click=True)

# gets table number and dealer name
def table_dealer(driver):
    tableNumber = findElement(driver, 'in-game', 'tableNumber')
    dealer = findElement(driver, 'in-game', 'dealer')
    return tableNumber.text, dealer.text

#a regex for extracting base64 data
def getBaseImage(cards, attribute, cardList):
    for card in cards:
        attValue = card.get_attribute(f'{attribute}')

        if 'card-hidden' not in attValue and 'base64' in attValue:
            pattern = r'.*?(?=iVBOR)|\); background-position: center center;$'
            getBase = re.sub(pattern, '', attValue)
            baseString = getBase.replace('background-position: center center;','')
            cardList.append(baseString)

#decode image and crop
def decodeCropImage(decoded, status):
    card = []
    for i, baseString in enumerate(decoded):
        base = base64.b64decode(baseString)
        getImage = Image.open(BytesIO(base))
        size = (10, 0, 80, 65)
        resizeImage = getImage.crop(size)
        resizeImage.save(f'screenshots\\decoded\\card {i}.png')
        value = tess.image_to_string(Image.open(f'screenshots\\decoded\\card {i}.png'), config='--psm 10')
        if str(value.replace('\n','')) in str(data('cards')):
            status.append(True)
            card.append(str(value.replace('\n','')))
        else:
            print(str(value.replace('\n',''), 'card value that is not in data("cards")'))
            status.append(False)

    return card

#extract cards data from history results
def betHistory(driver, game, status, cardResults, extracted):
    if game not in ['sedie', 'sicbo', 'roulette']:
        blueValue = []
        redValue = []
        selector = 'result-blue' if game != 'bull bull' else 'result-blue-bull'
        blueCards = findElements(driver, 'history', selector)
        redCards = findElements(driver, 'history', 'result-red')
        atrribute = 'class' if game != 'bull bull' else 'style'
        getBaseImage(blueCards, atrribute, blueValue)
        getBaseImage(redCards, 'class', redValue)
        flippedCards = cardResults + len(blueValue + redValue)
        #remove empty strings
        newItems = []
        newItems2 = []
        
        #repeated loop to get cards base64 sequence same as the results
        for blue in blueValue:
            if blue.strip():
                newItems.append(blue)

        for red in redValue:
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
    
#load and opens bet history records
def openBetHistory(driver, game, tableDealer, oldRow=0, updates=False):
    if game not in ['sedie', 'sicbo', 'roulette']:
        wait_If_Clickable(driver, 'history', 'button')
        waitElement(driver, 'history', 'modal')
        expand = findElement(driver, 'history', 'expand', status=True)

        if game not in ['sedie', 'sicbo', 'roulette']:
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

                for i in range(rowsAdded):
                    detail[i].click()
                    getTable = tableStage[i].text
                    waitElement(driver, 'history', 'result')
                    try:
                        baseList, flippedCards, extracted = betHistory(driver, game, status, flippedCards, extracted)
                    except:
                        ...                    
                    #creates log history for debugging in case of failure
                    with open('logs\\logs.txt', 'a') as logs:
                        newLine = '\n'
                        logs.write(f'Index {i} {getTable.replace(f"{newLine}"," ")} -'\
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

#function to test chatbox
def chat(driver, game, tableDealer):
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
        assertion(message, all(getLength), '==', True)
    
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
            
            print(f'{color}{status}{default} {message}')
            if not notice:
                GS_REPORT.append(['PASSED'])
        except AssertionError:
            print(f'{red}FAILED{default} {message}')
            if not notice:
                GS_REPORT.append(['FAILED'])
