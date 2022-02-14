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

    # Determine which version of PHP
    phpVersion = 0
    with open(phpPath, "r") as phpFile:
        phpFileContent = phpFile.read()
        if "session_start();" in phpFileContent:
            phpVersion = 1
        else:
            phpVersion = 2

    # Replace code in PHP files
    if phpVersion == 1:
        print("PHP Version 1")
        with open(phpPath, "r") as phpFile:
            phpFileContent = phpFile.read()
            # Replace the code
            phpFileContent = phpFileContent.replace(
                "session_start();\n",
                # add tab of the current line
                "session_start();\n                        $organism_images_root  = '../../../organism_images/';\n")

            phpFileContent = phpFileContent.replace(
                "$prevmap = '';\n",
                # add tab of the current line
                "$prevmap = '';\n" +
                "                        # Read csv - Sassan & Yuxin - Main/Blattodea/Archotermopsidae\n" +
                "                        $filenames = array();\n" +
                "                        $image_paths = array();\n\n" +
                "                        if (($handle = fopen(\"../../../db.csv\", \"r\")) !== FALSE) {\n" +
                "                          fgetcsv($handle);\n" +
                "                          while (($data = fgetcsv($handle, 1000, \", \")) !== FALSE) {\n" +
                "                            $num_cols = count($data);\n" +
                "                            if ($num_cols > 27) {\n" +
                "                              if ($data[52] == $order && $data[23] == $family) {\n" +
                "                                $file_sep = explode(\", \", $data[28]);\n" +
                "                                $image_path = $data[53];\n\n" +
                "                                $num = count($file_sep);\n\n" +
                "                                for ($c = 0; $c < $num; $c++) {\n" +
                "                                  if (strpos($file_sep[$c], '.jpg') !== false) {\n" +
                "                                    array_push($filenames, $file_sep[$c]);\n" +
                "                                    array_push($image_paths, $organism_images_root . $image_path);\n" +
                "                                  }\n" +
                "                                }\n" +
                "                              }\n" +
                "                            }\n" +
                "                          }\n" +
                "                          fclose($handle);\n" +
                "                        }\n\n" +
                "                        sort($filenames, SORT_STRING);\n" +
                "                        $i = 0;\n")

            phpFileContent = phpFileContent.replace(
                "                				foreach($files as $entry)\n",
                "                				foreach ($filenames as $entry)\n")

            phpFileContent = phpFileContent.replace(
                "                                    echo '		<a href=\"'.$entry.'\" class=\"image fit\"><img src=\"'.$entry.'\" alt=\"\" /></a>';\n",
                "                                    echo '		<a href=\"' . $image_paths[$i] . $entry . '\" class=\"image fit\"><img src=\"' . $image_paths[$i] . $entry . '\" alt=\"\" /></a>';\n")

            phpFileContent = phpFileContent.replace(
                "$lastmap = $mapfilename;\n\n\n                                }\n",
                "$lastmap = $mapfilename;\n\n\n                                }\n                                $i++;\n")

            # Write the file
            with open(phpPath, "w") as phpFile:
                phpFile.write(phpFileContent)

     # Replace code in PHP files
    if phpVersion == 2:
        print("PHP Version 2")
        with open(phpPath, "r") as phpFile:
            phpFileContent = phpFile.read()
            # Replace the code
            phpFileContent = phpFileContent.replace(
                "$prevname  = 'start';\n",
                # add tab of the current line
                "$prevname  = 'start';\n                        $organism_images_root  = '../../../organism_images/';\n")

            phpFileContent = phpFileContent.replace(
                "$prevmap = '';\n",
                # add tab of the current line
                "$prevmap = '';\n" +
                "                        # Read csv - Sassan & Yuxin - Main/Blattodea/Archotermopsidae\n" +
                "                        $filenames = array();\n" +
                "                        $image_paths = array();\n\n" +
                "                        if (($handle = fopen(\"../../../db.csv\", \"r\")) !== FALSE) {\n" +
                "                          fgetcsv($handle);\n" +
                "                          while (($data = fgetcsv($handle, 1000, \", \")) !== FALSE) {\n" +
                "                            $num_cols = count($data);\n" +
                "                            if ($num_cols > 27) {\n" +
                "                              if ($data[52] == $order && $data[23] == $family) {\n" +
                "                                $file_sep = explode(\", \", $data[28]);\n" +
                "                                $image_path = $data[53];\n\n" +
                "                                $num = count($file_sep);\n\n" +
                "                                for ($c = 0; $c < $num; $c++) {\n" +
                "                                  if (strpos($file_sep[$c], '.jpg') !== false) {\n" +
                "                                    array_push($filenames, $file_sep[$c]);\n" +
                "                                    array_push($image_paths, $organism_images_root . $image_path);\n" +
                "                                  }\n" +
                "                                }\n" +
                "                              }\n" +
                "                            }\n" +
                "                          }\n" +
                "                          fclose($handle);\n" +
                "                        }\n\n" +
                "                        sort($filenames, SORT_STRING);\n" +
                "                        $i = 0;\n")

            phpFileContent = phpFileContent.replace(
                "                				foreach($files as $entry)\n",
                "                				foreach ($filenames as $entry)\n")

            phpFileContent = phpFileContent.replace(
                "                                    echo '		<a href=\"'.$entry.'\" class=\"image fit\"><img src=\"'.$entry.'\" alt=\"\" /></a>';\n",
                "                                    echo '		<a href=\"' . $image_paths[$i] . $entry . '\" class=\"image fit\"><img src=\"' . $image_paths[$i] . $entry . '\" alt=\"\" /></a>';\n")

            phpFileContent = phpFileContent.replace(
                "$lastmap = $mapfilename;\n\n\n                                }\n",
                "$lastmap = $mapfilename;\n\n\n                                }\n                                $i++;\n")

            # Write the file
            with open(phpPath, "w") as phpFile:
                phpFile.write(phpFileContent)

    id += 1
