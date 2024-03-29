import csv
import re
from datetime import datetime
import logging


def write_csv(filename, data):
    """
    Write data/header into the csv file
    """
    with open(filename, "a", encoding="UTF8") as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(data)


RESULTS_CSV_FILENAME = "csv/results_03-15-2022 20.21.50.csv"
PROCESSED_CSV_HEADER = [
    "SEM #",
    "Path To Images",
    "Filenames"
]
FAILED_CSV_HEADER = [
    "id",
    "file_path",
    "image_file_name",
    "SEM_number_image",
    "SEM_number_image_conf",
    "scientific_name_filename",
    "SEM_number_filename",
    "angle_filename",
]


# Initialize time
now = datetime.now()
date_time = now.strftime("%m-%d-%Y %H.%M.%S")

# Initialize arrays
data_dict = {}

# Start logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = logging.FileHandler("log/log_processing_" + date_time + ".log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# Create results CSV file with header
processed_csv_filename = "csv/processed_" + date_time + ".csv"
write_csv(processed_csv_filename, PROCESSED_CSV_HEADER)

# Create failed CSV file with header
failed_csv_filename = "csv/failed_" + date_time + ".csv"
write_csv(failed_csv_filename, FAILED_CSV_HEADER)


# open up results csv file
with open(RESULTS_CSV_FILENAME, "r", encoding="UTF8") as f:
    reader = csv.reader(f)
    for row in reader:
        # skip header
        if row[0] == "id":
            continue

        # get the sem number
        sem_number = row[3]

        # test if sem number is valid using Regex
        pattern = "SEM-UBC [A-Z]{3,4}-[0-9]{3,5}"
        match = re.search(pattern, sem_number)

        # Fix the sem number
        try:
            # if sem number is valid without "SEM-UBC", extract rest and add "SEM-UBC"
            if match is None:
                pattern_without_sem_ubc = "[A-Z]{3,4}-[0-9]{3,5}"
                match = re.search(pattern_without_sem_ubc, sem_number)
                sem_extra = ""
                if match is not None:
                    sem_extra = match.group(0)

                # if space is in sem number last section, replace it with "-"
                if match is None:
                    pattern_without_sem_ubc = "[A-Z]{3,4} [0-9]{3,5}"
                    match = re.search(pattern_without_sem_ubc, sem_number)
                    if match is not None:
                        sem_extra = match.group(0).replace(" ", "-")

                    # if "- " is in sem number last section, replace it with "-"
                    if match is None:
                        pattern_without_sem_ubc = "[A-Z]{3,4}- [0-9]{3,5}"
                        match = re.search(pattern_without_sem_ubc, sem_number)
                        if match is not None:
                            sem_extra = match.group(0).replace("- ", "-")

                if match is not None:
                    logger.info(
                        "SEM number is valid without 'SEM-UBC': " + sem_extra)
                    sem_number = "SEM-UBC " + sem_extra

                # replace 0 with O
                sem_3_letters = sem_number.split("SEM-UBC ")[1].split("-")[0]
                if "0" in sem_3_letters:
                    logger.info(
                        "SEM number has 0 in 3 letters: " + sem_3_letters)
                    sem_3_letters = sem_3_letters.replace("0", "O")
                    sem_number = "SEM-UBC " + sem_3_letters + "-" + \
                        sem_number.split("SEM-UBC ")[1].split("-")[1]
                    match = re.search(pattern, sem_number)
        except:
            match = None

        # if not valid, skip but store in failed csv
        if match is None:
            logger.error("Sem number not valid: " + sem_number)
            write_csv(failed_csv_filename, row)
            continue

        # If the sem number is not in the data_dict, add it
        if sem_number not in data_dict:
            data_dict[sem_number] = {
                "SEM #": sem_number,
                "Path To Images": "",
                "Filenames": ""
            }

        # get photo path
        photo_path = row[1]
        photo_path = photo_path.replace("images/", "")
        photo_path = photo_path.replace(row[2], "")
        data_dict[sem_number]["Path To Images"] = photo_path

        # add filename
        data_dict[sem_number]["Filenames"] += row[2] + ", "


# write the data_dict to the processed csv file
for key in data_dict:
    write_csv(processed_csv_filename, data_dict[key].values())

logger.info("Done")
# go through each line and create an entry if SEM # is not in the csv file already
