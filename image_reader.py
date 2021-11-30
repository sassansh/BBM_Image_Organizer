import csv
import cv2
import io
import easyocr

# Open Image
image = cv2.imread(
    'example_images/Climaciella brunnea (2ventral).jpg', cv2.IMREAD_UNCHANGED)


# Pre processing
# Crop image
height, width, channels = image.shape
left = 0
top = int(height * 5.1 / 6)
right = width
bottom = int(height * 5.8 / 6)
image = image[top:bottom, left:right]

# Extract red channel
red_channel = image[:, :, 2]

# Preview image
# cv2.imshow('image', red_channel)
# cv2.waitKey(0)

# Covert Image to Byte Array
is_success, im_buf_arr = cv2.imencode(".jpg", red_channel)
byte_im = im_buf_arr.tobytes()

# Perform OCR on Image(Byte Array)
reader = easyocr.Reader(['en'])
result = reader.readtext(byte_im)
print(result)
