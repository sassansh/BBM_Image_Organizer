import csv
import cv2
import io
import easyocr
import os


with open('results.csv', 'a', encoding='UTF8') as f:
    header = ['filename', 'scientific_name_image', 'scientific_name_image_conf',
              'SEM_number_image', 'SEM_number_image_conf', 'angle_image', 'angle_image_conf',
              'scientific_name_filename', 'SEM_number_filename', 'angle_filename',
              'scientific_name_matches', 'SEM_number_matches', 'angle_matches', 'all_matches']

    writer = csv.writer(f)

    # write the header
    writer.writerow(header)


directory = 'example_images'
for imageName in os.listdir(directory):

    # Open Image
    image = cv2.imread(
        'example_images/' + imageName, cv2.IMREAD_UNCHANGED)

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
    reader = easyocr.Reader(['en'])
    result = reader.readtext(byte_im)
    print(result)

    # Extract red channel
    name_conf = result[0][2]
    sem_conf = result[1][2]

    if (name_conf < 0.5 or sem_conf < 0.5):
        print('Poor detection, trying red channel')
        red_channel = image[:, :, 2]

        # Covert Image to Byte Array
        is_success, im_buf_arr = cv2.imencode(".jpg", red_channel)
        byte_im = im_buf_arr.tobytes()

        # Perform OCR on Image(Byte Array)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(byte_im)
        print(result)

    # Prepare data from image
    filename = imageName
    scientific_name_image = result[0][1].split(' (')[0]
    scientific_name_image_conf = result[0][2]
    SEM_number_image = 'SEM' + result[1][1].split('SEM')[1]
    print(SEM_number_image)
    SEM_number_image_conf = result[1][2]
    angle_image = (result[0][1].split(' (')[1]).split(')')[0]
    angle_image_conf = result[0][2]

    # Prepare data from filename

    scientific_name_filename = imageName.split(' (')[0]
    SEM_number_filename = ''
    if 'SEM' in imageName:
        SEM_number_filename = 'SEM' + imageName.split('SEM')[1].split('.')[0]

    raw_angle_filename = imageName.split(' (')[1].split(')')[0]
    angle_filename = ''.join(i for i in raw_angle_filename if not i.isdigit())

    # Matching analysis
    angle_filename.replace(' ', '')
    angle_image.replace(' ', '')

    scientific_name_matches = str(
        scientific_name_filename == scientific_name_image)
    angle_matches = str(angle_filename == angle_image)

    if SEM_number_filename == '':
        SEM_number_matches = ''
    else:
        SEM_number_matches = str(SEM_number_filename == SEM_number_image)

     #   SEM_number_matches == '' ?
    if angle_matches == 'true' and scientific_name_matches == 'true' and (SEM_number_matches == 'true' or SEM_number_matches == ''):
        all_matches = 'true'
    else:
        all_matches = 'false'

    # Writing CSV

    data = [filename, scientific_name_image,
            scientific_name_image_conf, SEM_number_image, SEM_number_image_conf, angle_image, angle_image_conf,
            scientific_name_filename, SEM_number_filename, angle_filename,
            scientific_name_matches, SEM_number_matches, angle_matches, all_matches]

    with open('results.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)

        # write the data
        writer.writerow(data)
