import csv
import cv2
import io
import easyocr
import os
import re
from datetime import datetime
import glob


def read_image(image, top, bottom, left, right, filter, reader):
    """
    Perform OCR on image with given crop and filter
    """

    # Crop image
    image = image[top:bottom, left:right]

    filtered_image = image

    # Filter
    if filter == "red":
        # Red filter
        filtered_image = image[:, :, 2]

    # Preview image
    #cv2.imshow('image', filtered_image)
    # cv2.waitKey(0)

    # Covert Image to Byte Array
    is_success, im_buf_arr = cv2.imencode(".jpg", filtered_image)
    byte_im = im_buf_arr.tobytes()

    result = reader.readtext(byte_im)
    return result


# def parse_filename(imageName):
    """
    Read "scientific_name_filename,SEM_number_filename,angle_filename" from the given file
    """


# new main body
# set up the reader
now = datetime.now()
date_time = now.strftime("%m-%d-%Y %H.%M.%S")
reader = easyocr.Reader(['en'])

with open('results ' + date_time + '.csv', 'a', encoding='UTF8') as f:
    header = ['file_path', 'SEM_number_image', 'SEM_number_image_conf',
              'scientific_name_filename', 'SEM_number_filename', 'angle_filename']

    writer = csv.writer(f)

    # write the header
    writer.writerow(header)


directory = 'example_images/'
for imagePath in glob.iglob(directory + '**/*', recursive=True):
    # Extract filename
    imageFileName = os.path.basename(imagePath)

    now_image = datetime.now()
    date_time_image = now_image.strftime("%H:%M:%S")

    # Skip non-image files
    if not imageFileName.endswith(".jpg") and not imageFileName.endswith(".png") and not imageFileName.endswith(".jpeg"):
        continue

    print("\n========== STARTING: " + imagePath +
        " ========== " + date_time_image)

    # Prepare data from filename
    scientific_name_filename = ""
    SEM_number_filename = ""
    raw_angle_filename = ""
    angle_filename = ""



    try:
        scientific_name_filename = imageFileName.split(' (')[0]
        SEM_number_filename = ''
        if 'SEM' in imageFileName:
            SEM_number_filename = 'SEM' + \
                imageFileName.split('SEM')[1].split('.')[0]
        raw_angle_filename = imageFileName.split(' (')[1].split(')')[0]
        angle_filename = ''.join(
            i for i in raw_angle_filename if not i.isdigit())

        if SEM_number_filename == '':
            x = re.search("[A-Z]{2,}-[0-9]{3,}", imageFileName)
            try:
                SEM_number_filename = "SEM-UBC " + x.group()
                print("SEM Filename using REGEX: " + SEM_number_filename)
            except:
                SEM_number_filename = ""

    except Exception as e:
        print("ERROR:")
        print(e)
        print("Filename parsing failed for " + imagePath)
        scientific_name_filename = 'PARSING FAILED'
        SEM_number_filename = 'PARSING FAILED'
        angle_filename = 'PARSING FAILED'

    if SEM_number_filename == "" or SEM_number_filename == 'PARSING FAILED':
        # Open Image
        image = cv2.imread(
            imagePath, cv2.IMREAD_UNCHANGED)

        # Skip non-image files
        if not hasattr(image, 'shape'):
            continue

        # Try cropped image first
        height, width, channels = image.shape
        left = int(width * 3 / 5)
        top = int(height * 4.5 / 6)
        right = width
        bottom = height

        result_original = read_image(
            image, top, bottom, left, right, "none", reader)

        try:
            sem_conf_orignal = result_original[0][2]
        except:
            sem_conf_orignal = 0

        result = result_original
        original_better = True
        print("ORIGINAL OCR:")
        print(result_original)

        # Try cropped image with red filter
        if (sem_conf_orignal < 0.65):
            print('Poor detection, trying red channel')
            result_red = read_image(
                image, top, bottom, left, right, "red", reader)

            try:
                sem_conf_red = result_red[0][2]
                print("RED OCR:")
                print(result_red)
            except:
                sem_conf_red = 0

            if (sem_conf_red > sem_conf_orignal):
                result = result_red
                original_better = False

        if (original_better):
            print("Picking Original OCR")
        else:
            print("Picking Red OCR")

        # See if SEM number is in the cropped OCR
        SEM_exists = False
        for row in result:
            if 'SEM' in row[1].upper():
                SEM_exists = True
                print("SEM number detected in cropped OCR")
                break

        if (not SEM_exists):
            print("SEM number not detected in cropped OCR")
            print("Reading entire image dimentions...")
            # Try non-cropped original image
            left = 0
            top = 0
            right = width
            bottom = height

            result_original = read_image(
                image, top, bottom, left, right, "none", reader)

            try:
                sem_conf_orignal = result_original[0][2]
            except:
                sem_conf_orignal = 0

            result = result_original
            original_better = True
            print("WHOLE IMAGE (NO FILTER) OCR:")
            print(result_original)

            # Try cropped image with red filter
            if (sem_conf_orignal < 0.65):
                print('Poor detection, trying red channel')
                result_red = read_image(
                    image, top, bottom, left, right, "red", reader)

                try:
                    sem_conf_red = result_red[0][2]
                    print("WHOLE IMAGE (RED FILTER) OCR:")
                    print(result_red)
                except:
                    sem_conf_red = 0

                if (sem_conf_red > sem_conf_orignal):
                    result = result_red
                    original_better = False

            if (original_better):
                print("Picking Original OCR")
            else:
                print("Picking Red OCR")

        # empty all variables
        SEM_number_image = 'OCR FAILED'
        SEM_number_image_conf = '0'

        # Prepare data from image
        filename = imagePath

        try:
            for row in result:
                if 'SEM' in row[1].upper():
                    SEM_number_image = 'SEM' + row[1].upper().split('SEM')[1]
                    SEM_number_image_conf = row[2]
                    break
        except Exception as e:
            print("ERROR:")
            print(e)
            print("OCR failed for " + imagePath + "'s SEM_number")
            SEM_number_image = 'OCR FAILED'
            SEM_number_image_conf = '0'
    else:
        print("Skipping OCR, SEM number detected in filename")
        SEM_number_image = SEM_number_filename
        SEM_number_image_conf = "FROM FILENAME"

    # Writing CSV

    data = [imagePath, SEM_number_image, SEM_number_image_conf,
            scientific_name_filename, SEM_number_filename, angle_filename]

    with open('results ' + date_time + '.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)
    finish_image = datetime.now()
    date_time_image_finish = finish_image.strftime("%H:%M:%S")
    elapsed = finish_image - now_image
    print("Time to process file: " + str(elapsed))
    print("========== FINISHED: " + imagePath +
          " ========== " + date_time_image_finish + "\n")
