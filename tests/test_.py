from src.main import *
from src.modules import *


'''def test_DragonTiger(driver, lobby):
    play(driver, 'dragontiger', 'All')

def test_ThreeCards(driver, lobby):
    play(driver, 'three-cards', 'All')

def test_Sedie(driver, lobby):
    play(driver, 'sedie', 'All')'''

'''def test_Baccarat(driver):
    play(driver, 'baccarat', 'All')'''

'''def test_Allin_DragonTiger(driver, lobby):
    play(driver, 'dragontiger', 'Dragon', allin=True)'''

'''def test_Allin_ThreeCards(driver, lobby):
    play(driver, 'three-cards', 'Dragon', allin=True)'''

'''def test_Allin_Sedie(driver, lobby):
    play(driver, 'sedie', 'big', allin=True)'''

def test_Allin_Baccarat(driver):
    play(driver, 'baccarat', 'Banker', allin=True)