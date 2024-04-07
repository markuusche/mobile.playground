from src.main import *

def test_ThreeCards(driver, gsreport):
    play(driver, gsreport, 'three-cards', 'All', name='Three Cards')
    play(driver, gsreport, 'three-cards', 'Dragon', allin=True, name='Three Cards')

def test_Sedie(driver, gsreport):
    play(driver, gsreport, 'sedie', 'All', name='Sedie')
    play(driver, gsreport, 'sedie', 'big', allin=True, name='Sedie')

def test_Sicbo(driver, gsreport):
    play(driver, gsreport, 'sicbo', 'big', allin=True, name='Sicbo')

def test_Roulette(driver, gsreport):
    play(driver, gsreport, 'roulette', 'big', allin=True, name='Roulette')

def test_BullBull(driver, gsreport):
    play(driver, gsreport, 'bull bull', 'Z1 Double', allin=True, name='Bull Bull')

def test_DragonTiger(driver, gsreport):
    play(driver, gsreport, 'dragontiger', 'All', name='DT')
    play(driver, gsreport, 'dragontiger', 'Dragon', allin=True, name='DT')

def test_Baccarat(driver, gsreport):
    play(driver, gsreport, 'baccarat', 'All')
    play(driver, gsreport, 'baccarat', 'Banker', allin=True)
