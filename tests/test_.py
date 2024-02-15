from src.main import *
from src.modules import *

def test_ThreeCards_Allin_and_Odds(driver, lobby):
    play(driver, 'three-cards', 'All', name='Three Cards')
    play(driver, 'three-cards', 'Dragon', allin=True, name='Three Cards')

def test_Sedie_Allin_and_Odds(driver, lobby):
    play(driver, 'sedie', 'All', name='Sedie')
    play(driver, 'sedie', 'big', allin=True, name='Sedie')

def test_Sicbo_Allin(driver, lobby):
    play(driver, 'sicbo', 'big', allin=True, name='Sicbo')

def test_Roulette_Allin(driver, lobby):
    play(driver, 'roulette', 'big', allin=True, name='Roulette')

def test_DragonTiger_Allin_and_Odds(driver, lobby):
    play(driver, 'dragontiger', 'All', name='DT')
    play(driver, 'dragontiger', 'Dragon', allin=True, name='DT')

def test_Baccarat_Allin_and_Odds(driver, lobby):
    play(driver, 'baccarat', 'All')
    play(driver, 'baccarat', 'Banker', allin=True)
