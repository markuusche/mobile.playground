from src.main import *
from src.modules import *

def test_ThreeCards_Allin_and_Odds(driver, gsreport, lobby):
    play(driver, gsreport, 'three-cards', 'All', name='Three Cards')
    play(driver, gsreport, 'three-cards', 'Dragon', allin=True, name='Three Cards')

def test_Sedie_Allin_and_Odds(driver, gsreport, lobby):
    play(driver, gsreport, 'sedie', 'All', name='Sedie')
    play(driver, gsreport, 'sedie', 'big', allin=True, name='Sedie')

def test_Sicbo_Allin(driver, gsreport, lobby):
    play(driver, gsreport, 'sicbo', 'big', allin=True, name='Sicbo')

def test_Roulette_Allin(driver, gsreport, lobby):
    play(driver, gsreport, 'roulette', 'big', allin=True, name='Roulette')

def test_DragonTiger_Allin_and_Odds(driver, gsreport, lobby):
    play(driver, gsreport, 'dragontiger', 'All', name='DT')
    play(driver, gsreport, 'dragontiger', 'Dragon', allin=True, name='DT')

def test_Baccarat_Allin_and_Odds(driver, gsreport, lobby):
    play(driver, gsreport, 'baccarat', 'All')
    play(driver, gsreport, 'baccarat', 'Banker', allin=True)
