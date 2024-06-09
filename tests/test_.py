import pytest
from src.main import Main

@pytest.fixture
def main():
    return Main()

class Test():

    def test_threecards(self, main, driver, gsreport):
        main.play(driver, gsreport, 'three-cards', 'All', name='Three Cards')
        main.play(driver, gsreport, 'three-cards', allin=True, name='Three Cards')

    def test_sedie(self, main, driver, gsreport):
        main.play(driver, gsreport, 'sedie', 'All', name='Sedie')
        main.play(driver, gsreport, 'sedie', allin=True, name='Sedie')

    def test_sicbo(self, main, driver, gsreport):
        main.play(driver, gsreport, 'sicbo', allin=True, name='Sicbo')

    def test_roulette(self, main, driver, gsreport):
        main.play(driver, gsreport, 'roulette', allin=True, name='Roulette')

    def test_bullbull(self, main, driver, gsreport):
        main.play(driver, gsreport, 'bull bull', allin=True, name='Bull Bull')

    def test_dragontiger(self, main, driver, gsreport):
        main.play(driver, gsreport, 'dragontiger', 'All', name='DT')
        main.play(driver, gsreport, 'dragontiger', allin=True, name='DT')

    def test_baccarat(self, main, driver, gsreport):
        main.play(driver, gsreport, 'baccarat', 'All')
        main.play(driver, gsreport, 'baccarat', allin=True)
