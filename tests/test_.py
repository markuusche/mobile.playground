# pylint: disable=missing-function-docstring
from src.main import Main
from src.libs.modules import *

@pytest.fixture
def main():
    return Main()

class Test():

    def test_ThreeCards(self, driver, gsreport):
        main.play(driver, gsreport, 'three-cards', 'All', name='Three Cards')
        main.play(driver, gsreport, 'three-cards', allin=True, name='Three Cards')

    def test_Sedie(self, driver, gsreport):
        main.play(driver, gsreport, 'sedie', 'All', name='Sedie')
        main.play(driver, gsreport, 'sedie', allin=True, name='Sedie')

    def test_Sicbo(self, driver, gsreport):
        main.play(driver, gsreport, 'sicbo', allin=True, name='Sicbo')

    def test_Roulette(self, driver, gsreport):
        main.play(driver, gsreport, 'roulette', allin=True, name='Roulette')

    def test_BullBull(self, driver, gsreport):
        main.play(self, driver, gsreport, 'bull bull', allin=True, name='Bull Bull')

    def test_DragonTiger(self, driver, gsreport):
        main.play(driver, gsreport, 'dragontiger', 'All', name='DT')
        main.play(driver, gsreport, 'dragontiger', allin=True, name='DT')

    def test_Baccarat(self, driver, gsreport):
        main.play(driver, gsreport, 'baccarat', 'All')
        main.play(driver, gsreport, 'baccarat', allin=True)
