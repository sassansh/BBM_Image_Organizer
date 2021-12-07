import csv
import cv2
import io
import easyocr
import os
from datetime import datetime

now = datetime.now()

date_time = now.strftime("%m-%d-%Y %H.%M.%S")
reader = easyocr.Reader(['en'])

with open('results ' + date_time + '.csv', 'a', encoding='UTF8') as f:
    header = ['filename', 'scientific_name_image', 'scientific_name_image_conf',
              'SEM_number_image', 'SEM_number_image_conf', 'angle_image', 'angle_image_conf',
              'scientific_name_filename', 'SEM_number_filename', 'angle_filename',
              'scientific_name_matches', 'SEM_number_matches', 'angle_matches', 'all_matches']

    writer = csv.writer(f)

    # write the header
    writer.writerow(header)


directory = 'example_images'
for imageName in os.listdir(directory):

    print("========== STARTING: " + imageName + " ==========")

    # Skip non-image files
    if not imageName.endswith(".jpg") and not imageName.endswith(".png") and not imageName.endswith(".jpeg"):
        continue

    # Open Image
    image = cv2.imread(
        'example_images/' + imageName, cv2.IMREAD_UNCHANGED)

    # Skip non-image files
    if not hasattr(image, 'shape'):
        continue

    # Pre processing
    # Crop image
    height, width, channels = image.shape
    left = 0
    top = int(height * 5.1 / 6)
    right = width
    bottom = int(height * 5.8 / 6)
    image = image[top:bottom, left:right]

    # Preview image
    # cv2.imshow('image', red_channel)
    # cv2.waitKey(0)

    # Covert Image to Byte Array
    is_success, im_buf_arr = cv2.imencode(".jpg", image)
    byte_im = im_buf_arr.tobytes()

    # Perform OCR on Image(Byte Array)
    result_original = reader.readtext(byte_im)

    # Extract red channel
    try:
        name_conf_orignal = result_original[0][2]
        sem_conf_orignal = result_original[1][2]
    except:
        name_conf_orignal = 0
        sem_conf_orignal = 0

    result = result_original
    original_better = True
    print("ORIGINAL OCR:")
    print(result_original)

    if (name_conf_orignal < 0.65 or sem_conf_orignal < 0.65):
        print('Poor detection, trying red channel')
        red_channel = image[:, :, 2]

        # Covert Image to Byte Array
        is_success, im_buf_arr = cv2.imencode(".jpg", red_channel)
        byte_im = im_buf_arr.tobytes()

        # Perform OCR on Image(Byte Array)
        result_red = reader.readtext(byte_im)

        try:
            name_conf_red = result_red[0][2]
            sem_conf_red = result_red[1][2]
            print("RED OCR:")
            print(result_red)
        except:
            name_conf_red = 0
            sem_conf_red = 0

        if (name_conf_red > name_conf_orignal and sem_conf_red > sem_conf_orignal):
            result = result_red
            original_better = False

    if (original_better):
        print("Picking Original OCR")
    else:
        print("Picking Red OCR")

    # Prepare data from image
    filename = imageName

    try:
        scientific_name_image = result[0][1].split(' (')[0]
        scientific_name_image_conf = result[0][2]
        SEM_number_image = 'SEM' + result[1][1].upper().split('SEM')[1]
        SEM_number_image_conf = result[1][2]
        angle_image = (result[0][1].split(' (')[1]).split(')')[0]
        angle_image_conf = result[0][2]
    except Exception as e:
        print(e)
        print("OCR failed for " + imageName)
        scientific_name_image = 'OCR FAILED'
        scientific_name_image_conf = '0'
        SEM_number_image = 'OCR FAILED'
        SEM_number_image_conf = '0'
        angle_image = 'OCR FAILED'
        angle_image_conf = '0'

    # Prepare data from filename

    try:
        scientific_name_filename = imageName.split(' (')[0]
        SEM_number_filename = ''
        if 'SEM' in imageName:
            SEM_number_filename = 'SEM' + \
                imageName.split('SEM')[1].split('.')[0]

        raw_angle_filename = imageName.split(' (')[1].split(')')[0]
        angle_filename = ''.join(
            i for i in raw_angle_filename if not i.isdigit())
    except Exception as e:
        print(e)
        print("Filename parsing failed for " + imageName)
        scientific_name_filename = 'PARSING FAILED'
        SEM_number_filename = 'PARSING FAILED'
        raw_angle_filename = 'PARSING FAILED'
        angle_filename = 'PARSING FAILED'

    # Matching analysis

    scientific_name_matches = str(scientific_name_filename.replace(" ", "").lower()
                                  == scientific_name_image.replace(" ", "").lower())
    angle_matches = str(angle_filename.replace(" ", "").lower()
                        == angle_image.replace(" ", "").lower())

    if SEM_number_filename == '':
        SEM_number_matches = ''
    else:
        SEM_number_matches = str(SEM_number_filename.replace(" ", "").lower()
                                 == SEM_number_image.replace(" ", "").lower())

    if angle_matches == "True" and scientific_name_matches == "True" and (SEM_number_matches == "True" or SEM_number_matches == ''):
        all_matches = 'True'
    else:
        all_matches = 'False'

    # Writing CSV

    data = [filename, scientific_name_image,
            scientific_name_image_conf, SEM_number_image, SEM_number_image_conf, angle_image, angle_image_conf,
            scientific_name_filename, SEM_number_filename, angle_filename,
            scientific_name_matches, SEM_number_matches, angle_matches, all_matches]

    with open('results ' + date_time + '.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)
    print("========== FINISHED: " + imageName + " ==========\n\n")
