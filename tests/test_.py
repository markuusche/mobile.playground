import pytest
from src.main import Main

@pytest.fixture
def main():
    return Main()

class Test():

    def test_threecards(self, main, driver, gsreport):
        main.play(driver, gsreport, 'three-cards', name='Three Cards')

    def test_sedie(self, main, driver, gsreport):
        main.play(driver, gsreport, 'sedie', name='Sedie')

    def test_sicbo(self, main, driver, gsreport):
        main.play(driver, gsreport, 'sicbo', name='Sicbo')

    def test_roulette(self, main, driver, gsreport):
        main.play(driver, gsreport, 'roulette', name='Roulette')

    def test_bullbull(self, main, driver, gsreport):
        main.play(driver, gsreport, 'bull bull', name='Bull Bull')

    def test_dragontiger(self, main, driver, gsreport):
        main.play(driver, gsreport, 'dragontiger', name='DT')

    def test_baccarat(self, main, driver, gsreport):
        main.play(driver, gsreport, 'baccarat', name='Baccarat')
