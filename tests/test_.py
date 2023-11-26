from src.game import *
from src.modules import *

def test_Baccarat_Betting(driver):
    play(driver, 'baccarat', 'Player', allin=True)
