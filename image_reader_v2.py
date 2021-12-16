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
    # cv2.imshow('image', filtered_image)
    # cv2.waitKey(0)

    # Covert Image to Byte Array
    is_success, im_buf_arr = cv2.imencode(".jpg", filtered_image)
    byte_im = im_buf_arr.tobytes()

    result = reader.readtext(byte_im)
    return result


def write_csv(filename, data):
    """
    Write data/header into the csv file
    """
    with open(filename, "a", encoding="UTF8") as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(data)


def parse_filename(filename):
    """
    Read "scientific_name_filename,SEM_number_filename,angle_filename" from the given file
    """
    # Prepare data from filename
    scientific_name = ""
    SEM_number = ""
    raw_angle = ""
    angle = ""

    try:
        scientific_name = filename.split(" (")[0]
        SEM_number = ""
        if "SEM" in filename:
            SEM_number = "SEM" + filename.split("SEM")[1].split(".")[0]
        raw_angle = filename.split(" (")[1].split(")")[0]
        angle = "".join(i for i in raw_angle if not i.isdigit())

        if SEM_number == "":
            x = re.search("[A-Z]{2,}-[0-9]{3,}", filename)
            try:
                SEM_number = "SEM-UBC " + x.group()
            except:
                SEM_number = ""

    except Exception as e:
        print("ERROR:")
        print(e)
        print("Filename parsing failed for " + imagePath)
        scientific_name = "PARSING FAILED"
        SEM_number = "PARSING FAILED"
        angle = "PARSING FAILED"

    return scientific_name, SEM_number, angle


def find_SEM_conf(result):
    """
    Find the confidence of the SEM number
    """
    conf = 0

    for row in result:
        if "SEM" in row[1].upper():
            conf = row[2]
            break

    return conf


def SEM_exists(result):
    """
    Return True if the result contains a SEM number
    """
    exists = False

    for row in result:
        if "SEM" in row[1].upper():
            exists = True
            break

    return exists


def cropped_scan(image, filter, reader):
    """
    Perform OCR on bottom right corner of image using original filter
    """
    # Set crop dimensions
    height, width, channels = image.shape
    left = int(width * 3 / 5)
    top = int(height * 4.5 / 6)
    right = width
    bottom = height

    # Perform OCR
    result = read_image(image, top, bottom, left, right, filter, reader)

    # Get SEM confidence
    conf = find_SEM_conf(result)

    return result, conf


def full_scan(image, filter, reader):
    """
    Perform OCR on the whole image using original filter
    """
    # Set crop dimensions
    height, width, channels = image.shape
    left = 0
    top = 0
    right = width
    bottom = height

    # Perform OCR
    result = read_image(image, top, bottom, left, right, filter, reader)

    # Get SEM confidence
    conf = find_SEM_conf(result)

    return result, conf


def parse_result(result):
    """
    Parse the SEM number from the selected result
    and put 'OCR FAILED' if it causes error.
    """
    SEM_number = "OCR FAILED"

    try:
        for row in result:
            if "SEM" in row[1].upper():
                SEM_number = "SEM" + row[1].upper().split("SEM")[1]
                break
    except Exception as e:
        print("ERROR:")
        print(e)
        print("OCR failed for " + imagePath + "'s SEM_number")
        SEM_number = "OCR FAILED"

    return SEM_number


# Main Body
# Global Static Variables
MIN_CONFIDENCE = 0.75
IMAGES_ROOT_DIRECTORY = "example_images/"
CSV_HEADER = [
    "file_path",
    "image_file_name",
    "SEM_number_image",
    "SEM_number_image_conf",
    "scientific_name_filename",
    "SEM_number_filename",
    "angle_filename",
]

# Initialize time & OCR Reader
now = datetime.now()
date_time = now.strftime("%m-%d-%Y %H.%M.%S")
reader = easyocr.Reader(["en"])

# Create results CSV file with header
results_csv_filename = "results_" + date_time + ".csv"
write_csv(results_csv_filename, CSV_HEADER)

# Read all images in the directory
for imagePath in glob.iglob(IMAGES_ROOT_DIRECTORY + "**/*", recursive=True):
    # Initialize variables
    sem_conf_cropped_red = 0
    sem_conf_cropped_orignal = 0
    sem_conf_full_red = 0
    sem_conf_full_orignal = 0
    scientific_name_filename = ""
    SEM_number_filename = ""
    angle_filename = ""

    # Extract filename
    imageFileName = os.path.basename(imagePath)

    now_image = datetime.now()
    date_time_image = now_image.strftime("%H:%M:%S")

    # Skip non-image files
    if (
        not imageFileName.endswith(".jpg")
        and not imageFileName.endswith(".png")
        and not imageFileName.endswith(".jpeg")
    ):
        continue

    print("\n========== STARTING: " + imagePath + " ========== " + date_time_image)

    # Parse filename
    scientific_name_filename, SEM_number_filename, angle_filename = parse_filename(
        imageFileName
    )

    # Perform OCR if filename doesn't contain the SEM number
    if SEM_number_filename == "" or SEM_number_filename == "PARSING FAILED":
        # Open Image
        image = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)

        # Skip non-image files
        if not hasattr(image, "shape"):
            continue

        # Perform cropped original OCR
        result_original, sem_conf_cropped_orignal = cropped_scan(
            image, "original", reader
        )

        result = result_original
        print("ORIGINAL OCR:")
        print(result_original)

        # If low confidence, try red filter
        if sem_conf_cropped_orignal < MIN_CONFIDENCE:
            print("Poor detection, trying red channel")
            # Perform cropped red OCR
            result_red, sem_conf_cropped_red = cropped_scan(image, "red", reader)

            print("RED OCR:")
            print(result_red)

        # Compare original and red OCR results
        if sem_conf_cropped_red > sem_conf_cropped_orignal:
            print("Picking Red OCR")
            result = result_red
        else:
            print("Picking Original OCR")

        # See if SEM number is in the cropped OCR
        SEM_exists_in_result = SEM_exists(result)

        # If SEM number is not in the cropped OCR, perform full OCR
        if not SEM_exists_in_result:
            print("SEM number not detected in cropped OCR")
            print("Reading entire image dimentions...")
            # Try non-cropped original image
            result_original, sem_conf_full_original = full_scan(
                image, "original", reader
            )

            result = result_original
            original_better = True
            print("WHOLE IMAGE (NO FILTER) OCR:")
            print(result_original)

            # If low confidence, try red filter
            if sem_conf_full_original < MIN_CONFIDENCE:
                print("Poor detection, trying red channel")
                result_red, sem_conf_full_red = full_scan(image, "red", reader)

                print("WHOLE IMAGE (RED FILTER) OCR:")
                print(result_red)

            if sem_conf_full_red > sem_conf_full_original:
                print("Picking Red OCR")
                result = result_red
            else:
                print("Picking Original OCR")

        # Parse SEM number
        SEM_number_image_conf = find_SEM_conf(result)
        SEM_number_image = parse_result(result)

    else:
        print("Skipping OCR, SEM number detected in filename")
        SEM_number_image = SEM_number_filename
        SEM_number_image_conf = "FROM FILENAME"

    # Writing CSV
    data = [
        imagePath,
        imageFileName,
        SEM_number_image,
        SEM_number_image_conf,
        scientific_name_filename,
        SEM_number_filename,
        angle_filename,
    ]
    write_csv(results_csv_filename, data)

    finish_image = datetime.now()
    date_time_image_finish = finish_image.strftime("%H:%M:%S")
    elapsed = finish_image - now_image
    print("Time to process file: " + str(elapsed))
    print(
        "========== FINISHED: "
        + imagePath
        + " ========== "
        + date_time_image_finish
        + "\n"
    )
