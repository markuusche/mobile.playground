from src.main import Main

class Test(Main):
    def test_ThreeCards(self, driver, gsreport):
        self.play(driver, gsreport, 'three-cards', 'All', name='Three Cards')
        self.play(driver, gsreport, 'three-cards', allin=True, name='Three Cards')

    def test_Sedie(self, driver, gsreport):
        self.play(driver, gsreport, 'sedie', 'All', name='Sedie')
        self.play(driver, gsreport, 'sedie', allin=True, name='Sedie')

    def test_Sicbo(self, driver, gsreport):
        self.play(driver, gsreport, 'sicbo', allin=True, name='Sicbo')

    def test_Roulette(self, driver, gsreport):
        self.play(driver, gsreport, 'roulette', allin=True, name='Roulette')

    def test_BullBull(self, driver, gsreport):
        self.play(self, driver, gsreport, 'bull bull', allin=True, name='Bull Bull')

    def test_DragonTiger(self, driver, gsreport):
        self.play(driver, gsreport, 'dragontiger', 'All', name='DT')
        self.play(driver, gsreport, 'dragontiger', allin=True, name='DT')

    def test_Baccarat(self, driver, gsreport):
        self.play(driver, gsreport, 'baccarat', 'All')
        self.play(driver, gsreport, 'baccarat', allin=True)
