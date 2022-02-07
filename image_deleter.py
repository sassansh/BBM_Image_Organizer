import os
import re
from datetime import datetime
import glob
import shutil
import logging


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
        logger.info("ERROR:")
        logger.info(e)
        logger.info("Filename parsing failed for " + imagePath)
        scientific_name = "PARSING FAILED"
        SEM_number = "PARSING FAILED"
        angle = "PARSING FAILED"

    return scientific_name, SEM_number, angle


# Main Body
# Global Static Variables
IMAGES_ROOT_DIRECTORY = "Main/"


# Initialize time & OCR Reader
id = 0
now = datetime.now()
date_time = now.strftime("%m-%d-%Y %H.%M.%S")

# Start logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = logging.FileHandler("log_deleter_" + date_time + ".log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


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

    # Ignore file if starts with "_"
    if imageFileName.startswith("_"):
        continue

    now_image = datetime.now()
    date_time_image = now_image.strftime("%H:%M:%S")

    # Skip non-image files
    if (
        not imageFileName.endswith(".jpg")
        and not imageFileName.endswith(".png")
        and not imageFileName.endswith(".jpeg")
    ):
        continue

    logger.info(
        "\n====ID: "
        + str(id)
        + "====== STARTING: "
        + imagePath
        + " ========== "
        + date_time_image
    )

    # Parse filename
    scientific_name_filename, SEM_number_filename, angle_filename = parse_filename(
        imageFileName
    )

    # If no angle, ignore file
    if angle_filename == "PARSING FAILED":
        continue

    # If angle EtOH, ignore file
    if angle_filename == "EtOH":
        continue

    # Copy the image to a new folder

    original = imagePath
    os.remove(original)

    finish_image = datetime.now()
    date_time_image_finish = finish_image.strftime("%H:%M:%S")
    elapsed = finish_image - now_image
    logger.info("Time to process file: " + str(elapsed))
    logger.info(
        "========== FINISHED: "
        + imagePath
        + " ========== "
        + date_time_image_finish
        + "\n"
    )

    id += 1
