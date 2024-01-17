from src.main import *
from src.modules import *

def test_ThreeCards_Allin_and_Odds(driver, lobby):
    play(driver, 'three-cards', 'All')
    play(driver, 'three-cards', 'Dragon', allin=True)

def test_Sedie_Allin_and_Odds(driver, lobby):
    play(driver, 'sedie', 'All')
    play(driver, 'sedie', 'big', allin=True)

def test_DragonTiger_Allin_and_Odds(driver, lobby):
    play(driver, 'dragontiger', 'All')
    play(driver, 'dragontiger', 'Dragon', allin=True)

def test_Baccarat_Allin_and_Odds(driver):
    play(driver, 'baccarat', 'All')
    play(driver, 'baccarat', 'Banker', allin=True)