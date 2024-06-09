import re
import os
import sys
import base64
import pytesseract

from PIL import Image
from io import BytesIO
from src.utils.utils import Utilities

if sys.platform.startswith('linux'):
    path = '/usr/bin/tesseract'
else:
    deviceName = os.environ['USERPROFILE'].split(os.path.sep)[-1]
    path = f'C:\\Users\\{deviceName}\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

pytesseract.pytesseract.tesseract_cmd = path

class Decoder:
    
    def __init__(self) -> None:
        self.utils = Utilities()
    
    def base64_encoded(self, cards, attribute, cardList):
        """
        Extract base64 encoded images from the given list of cards.

        params:
        `cards` (list): A list of card elements.
        `attribute` (str): The attribute to retrieve from the card elements.
        `cardlist` (list): An empty list to store the extracted base64 encoded images.

        : Iterate through the list of card elements.
        : Extract the specified attribute value from each card element.
        : If the attribute value indicates that the card is not hidden and contains a base64 encoded image,
        : extract the base64 encoded image and append it to the provided cardlist.
        """

        for card in cards:
            attValue = card.get_attribute(f'{attribute}')

            if 'card-hidden' not in attValue and 'base64' in attValue:
                pattern = r'iVBOR[^"]+'
                matches = re.findall(pattern, attValue)
                if matches:
                    base64 = matches[0]
                    cardList.append(base64)

    def decode_base64_card(self, decoded, status):
        """
        Decode and crop images from base64 encoded strings.

        params:
        `decoded` (list): A list of base64 encoded image strings.
        `status` (list): An empty list to store the status of each decoded image.

        : Iterate through the list of decoded base64 encoded image strings.
        : Decode each base64 encoded string and open it as an image.
        : Crop the image to a specific size.
        : Save the cropped image to a file.
        : Use Tesseract OCR to extract the text value from the cropped image.
        : Check if the extracted text value is present in the predefined list of cards.
        : Append the status of each card extraction to the status list.
        : Return a list of extracted card values.
        """

        card = []
        for index, baseString in enumerate(decoded):
            base = base64.b64decode(baseString)
            getImage = Image.open(BytesIO(base))
            size = (10, 0, 80, 65)
            resizeImage = getImage.crop(size)
            resizeImage.save(f'screenshots\\decoded\\card {index}.png')
            value = pytesseract.image_to_string(Image.open(f'screenshots\\decoded\\card {index}.png'), config='--psm 10')
            if str(value.replace('\n','')) in str(self.utils.data('cards')):
                status.append(True)
                card.append(str(value.replace('\n','')))
            else:
                print(str(value.replace('\n',''), 'card value that is not in data("cards")'))
                status.append(False)

        return card