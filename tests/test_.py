from src.game import *
from src.modules import *

def test_Baccarat(driver):
    play(driver, 'baccarat', 'Banker', allin=True)

def test_DragonTiger(driver):
    play(driver, 'dragontiger', 'Dragon', allin=True)

def test_ThreeCards(driver):
    play(driver, 'three-cards', 'Dragon', allin=True)

def test_Sedie(driver):
    play(driver, 'sedie', 'big', allin=True)
