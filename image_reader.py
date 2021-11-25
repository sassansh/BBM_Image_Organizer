# read image
from PIL import Image
# csv
import csv

# scan image
import easyocr
# im = Image.open('Albuna pyramidalis coloradensis female (1dorsal).jpg')
# print(im)
reader = easyocr.Reader(['en'])
result = reader.readtext(
    'example_images/Albuna pyramidalis coloradensis female (1dorsal).jpg')
print(result)
