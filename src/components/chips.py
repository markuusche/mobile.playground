import random

from src import BET_LIMIT
from src.helpers.helpers import Helpers

class Chips(Helpers):

    def __init__(self) -> None:
        super().__init__()
        
    def get_chip_value(self, driver):
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
        chips_placed = self.search_elements(driver, 'in-game', 'totalMoney')
        for chip in chips_placed:
            if chip.text != '':
                chips += float(chip.text.replace(',',''))

        return chips
    
    def edit_chips(self, driver, divide=10, add=False, amount=0):
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
        
        balance = self.search_element(driver, 'in-game', 'balance')
        user_balance = float(balance.text.replace(',',''))

        if add:
            chips = amount
        else:
            chips = int(user_balance) / divide - 1
            limit = BET_LIMIT[0]
            if chips < limit:
                chip_value = random.randint(limit, limit + 99)
                chips = chip_value
        
        self.wait_clickable(driver, 'in-game', 'edit')
        self.wait_element(driver, 'in-game', 'chip amount')
        self.wait_clickable(driver, 'in-game', 'edit button')
        self.wait_clickable(driver, 'in-game', 'clear')
        input = self.search_element(driver, 'in-game', 'input chips')
        input.send_keys(int(chips))
        self.wait_clickable(driver, 'in-game', 'save amount')
        self.wait_clickable(driver, 'in-game', 'payrate-close')
        self.wait_element_invisibility(driver, 'in-game', 'chip amount')
