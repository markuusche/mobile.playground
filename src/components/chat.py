import pyperclip
import grapheme

from faker import Faker
fake = Faker()
from src.utils.utils import Utilities
from src.helpers.helpers import Helpers
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class Chat(Helpers):

    def __init__(self) -> None:
        super().__init__()
        self.utils = Utilities()
    
    def chatbox(self, driver, game, tableDealer):
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
            self.wait_clickable(driver, 'chat', 'button')
            self.wait_text_element(driver, 'chat', 'send', text='Send', timeout=3)
            sendMessage = self.search_element(driver, 'chat', 'input')
            cn = Faker(['zh_TW'])
            getLength = []
            while True:
                sendMessage.send_keys(cn.text())
                self.wait_clickable(driver, 'chat', 'send')
                for _ in range(10):
                    pyperclip.copy(fake.emoji())
                    action = ActionChains(driver)
                    action.key_down(Keys.CONTROL).send_keys("v")
                    action.key_up(Keys.CONTROL).perform()

                self.wait_clickable(driver, 'chat', 'send')
                text = self.search_elements(driver, 'chat', 'messages')
                sendMessage.send_keys(fake.text())
                self.wait_clickable(driver, 'chat', 'send')
                message = self.utils.debuggerMsg(tableDealer, 'Chatbox messages are displayed or not empty')
                self.utils.assertion(message, len(text), '!=', 0)
                for msg in text:
                    textCount = sum(1 for _ in grapheme.graphemes(msg.text.strip()))
                    if textCount <= 22:
                        getLength.append(True)
                    else:
                        getLength.append(False)
                        print(msg.text, len(msg.text))
                break

            message = self.utils.debuggerMsg(tableDealer, 'Chat messages sent does not exceed 22 characters')
            self.utils.assertion(message, all(getLength))
