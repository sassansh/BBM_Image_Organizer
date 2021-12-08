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

    now_image = datetime.now()
    date_time_image = now_image.strftime("%H:%M:%S")

    print("========== STARTING: " + imageName +
          " ========== " + date_time_image)

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
    top = int(height * 4.5 / 6)
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

    # empty all variables
    scientific_name_image = ''
    scientific_name_image_conf = ''
    SEM_number_image = 'OCR FAILED'
    SEM_number_image_conf = '0'
    angle_image = ''
    angle_image_conf = ''
    scientific_name_filename = ''
    SEM_number_filename = ''
    angle_filename = ''
    scientific_name_matches = ''
    SEM_number_matches = ''
    angle_matches = ''
    all_matches = ''

    # Prepare data from image
    filename = imageName

    try:
        scientific_name_image = result[0][1].split('(')[0].rstrip()
        scientific_name_image_conf = result[0][2]
        angle_image = (result[0][1].split('(')[1]).split(')')[0]
        angle_image_conf = result[0][2]
    except Exception as e:
        print("ERROR:")
        print(e)
        print("OCR failed for " + imageName +
              "'s name or angle... trying combining array")
        try:
            combine_name_angle = ''
            combine_name_angle_conf = 0
            i = 0
            while i < len(result):
                if ('SEM' not in result[i][1]):
                    combine_name_angle += result[i][1] + ' '
                    combine_name_angle_conf += result[i][2]
                i += 1
            combine_name_angle_conf = combine_name_angle_conf / i
            scientific_name_image = combine_name_angle.split('(')[0].rstrip()
            scientific_name_image_conf = combine_name_angle_conf
            angle_image = (combine_name_angle.split('(')[1]).split(')')[0]
            angle_image_conf = combine_name_angle_conf
        except Exception as e:
            print("ERROR:")
            print(e)
            print("OCR failed for" + imageName + "'s name or angle")
            scientific_name_image = 'OCR FAILED'
            scientific_name_image_conf = '0'
            angle_image = 'OCR FAILED'
            angle_image_conf = '0'

    # Convert capital I to l
    if ("I" in scientific_name_image[1:] and scientific_name_image != 'OCR FAILED'):
        print("Replacing I with l")
        scientific_name_image = scientific_name_image[0] + \
            scientific_name_image[1:].replace("I", "l")

    # Convert € to C
    print("Replacing € with C")
    scientific_name_image = scientific_name_image.replace("€", "C")

    try:
        for row in result:
            if 'SEM' in row[1]:
                SEM_number_image = 'SEM' + row[1].upper().split('SEM')[1]
                SEM_number_image_conf = row[2]
                break
    except Exception as e:
        print("ERROR:")
        print(e)
        print("OCR failed for " + imageName + "'s SEM_number")
        SEM_number_image = 'OCR FAILED'
        SEM_number_image_conf = '0'

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
        print("ERROR:")
        print(e)
        print("Filename parsing failed for " + imageName)
        scientific_name_filename = 'PARSING FAILED'
        SEM_number_filename = 'PARSING FAILED'
        raw_angle_filename = 'PARSING FAILED'
        angle_filename = 'PARSING FAILED'

    # Determine if extra characters are present in OCR name
    if scientific_name_filename in scientific_name_image:
        print("Scientific name in OCRed name, replacing OCR name(" +
              scientific_name_image + ") with filename")
        scientific_name_image = scientific_name_filename

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
    finish_image = datetime.now()
    date_time_image_finish = finish_image.strftime("%H:%M:%S")
    elapsed = finish_image - now_image
    print("Time to complete OCR: " + str(elapsed))
    print("========== FINISHED: " + imageName +
          " ========== " + date_time_image_finish + "\n\n")
