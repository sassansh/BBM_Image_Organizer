# Script to find all PHP files for organisms and modify them to use the DB to load images paths and filenames
import os
import sys
import re
import argparse
import shutil
import glob
import time
from datetime import datetime
import logging


# Main Body
# Global Static Variables
PHP_ROOT_DIRECTORY = "website/Main/"


# Initialize time
id = 0
now = datetime.now()
date_time = now.strftime("%m-%d-%Y %H.%M.%S")

# Start logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

fh = logging.FileHandler("log_php_modifier_" + date_time + ".log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


# Read all phps in the directory
for phpPath in glob.iglob(PHP_ROOT_DIRECTORY + "**/*", recursive=True):
    # Extract filename
    phpFileName = os.path.basename(phpPath)

    now_php = datetime.now()
    date_time_php = now_php.strftime("%H:%M:%S")

    # Skip if file not named index.php
    if not phpFileName == "index.php":
        continue

    logger.info(
        "\n====ID: "
        + str(id)
        + "====== "
        + phpPath
        + " ========== "
        + date_time_php
    )

    # Read the PHP and make it includes "<title><?php echo ucwords(basename(dirname(__FILE__))); ?></title>"
    with open(phpPath, "r") as phpFile:
        phpFileContent = phpFile.read()
        if "<title><?php echo ucwords(basename(dirname(__FILE__))); ?></title>" not in phpFileContent:
            logger.info("Skipping " + phpPath)
            continue

    # Replace code in PHP files
    with open(phpPath, "r") as phpFile:
        phpFileContent = phpFile.read()
        # Replace the code
        phpFileContent = phpFileContent.replace(
            "$path = '../../../../../';\n  }\n",
            # add tab of the current line
            "$path = '../../../../../';\n  }\n\n  include $path . 'php/database-image-lookup.php';\n\n")
        phpFileContent = phpFileContent.replace(
            "$prevmap = '';\n",
            "$prevmap = '';\n\n                        $organism_images = SearchDatabaseForImages($family, $order, $path);\n\n")

        phpFileContent = phpFileContent.replace(
            "                				foreach($files as $entry)\n",
            "                				foreach ($organism_images as $entry)\n")

        phpFileContent = phpFileContent.replace(
            "$entryext = pathinfo($entry, PATHINFO_EXTENSION);",
            "$entryext = pathinfo($entry->filename, PATHINFO_EXTENSION);")
        phpFileContent = phpFileContent.replace(
            "if ($entry != \".\" && $entry != \"..\"  && $entryext == \"jpg\") {",
            "if ($entry->filename != \".\" && $entry->filename != \"..\"  && $entryext == \"jpg\") {")
        phpFileContent = phpFileContent.replace(
            "$chunks = explode(\" (\", $entry);",
            "$chunks = explode(\" (\", $entry->filename);")

        phpFileContent = phpFileContent.replace(
            "                                    echo '		<a href=\"'.$entry.'\" class=\"image fit\"><img src=\"'.$entry.'\" alt=\"\" /></a>';\n",
            "                                    echo '		<a href=\"' . $entry->filepath . $entry->filename . '\" class=\"image fit\"><img src=\"' . $entry->filepath . $entry->filename . '\" alt=\"\" /></a>';\n")

        # Write the file
        with open(phpPath, "w") as phpFile:
            phpFile.write(phpFileContent)
    id += 1
