from src.game import *
from src.modules import *


'''def test_DragonTiger(driver):
    play(driver, 'dragontiger', 'All')'''

'''def test_ThreeCards(driver):
    play(driver, 'three-cards', 'All')

def test_Sedie(driver):
    play(driver, 'sedie', 'All')

def test_Baccarat(driver):
    play(driver, 'baccarat', 'All')'''

def test_Allin_DragonTiger(driver):
    play(driver, 'dragontiger', 'Dragon', allin=True)

'''def test_Allin_ThreeCards(driver):
    play(driver, 'three-cards', 'Dragon', allin=True)

def test_Allin_Sedie(driver):
    play(driver, 'sedie', 'big', allin=True)

def test_Allin_Baccarat(driver):
    play(driver, 'baccarat', 'Banker', allin=True)'''