from PIL import Image
import csv
import cv2
import io
import easyocr

# Open Image
# im = Image.open('example_images/Leptomantispa pulchella (3lateral).jpg')
image = cv2.imread("example_images/Albuna pyramidalis coloradensis female (1dorsal).jpg")
# height, width, channels = im.shape
# Pre processing
# Crop image
# left = 0
# top = int(height * 4 / 5)
# right = width
# bottom = height 
# cropped_image = im.crop((left, top, right, bottom))
# print(top)
# crop_img = im[top:bottom, left:right]
# cv2.imshow("cropped", crop_img)
# resize the image


# change to grayscale
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
cv2.imshow('image',image)
cv2.waitKey(0)
# remove noise
#

# Covert Image to Byte Array
#img_byte_arr = io.BytesIO()
#cropped_image.save(img_byte_arr, format='JPEG')
#img_byte_arr = img_byte_arr.getvalue()
is_success, im_buf_arr = cv2.imencode(".jpg", image)
byte_im = im_buf_arr.tobytes()

# Perform OCR on Image(Byte Array)
reader = easyocr.Reader(['en'])
result = reader.readtext(byte_im)
print(result)
