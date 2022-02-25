<?php

use airmoi\FileMaker\FileMaker;
use airmoi\FileMaker\FileMakerException;

function SearchDatabaseForImages($family, $order, $path)
{
    class OrganismImage
    {
        public $filename;
        public $filepath;
    }
    require($path . 'autoloader.php');

    #TODO: Load credentials from a file
    $fm = new FileMaker('test.fmp12', 'collections.zoology.ubc.ca', 'Webuser', '12345');
    $organism_images_root  = $path . 'organism_images/';
    $organism_images = array();

    try {
        $command = $fm->newFindCommand('Spencer Entomological Collection');
        $command->addFindCriterion('Family', $family);
        $command->addFindCriterion('Order', $order);
        $records = $command->execute()->getRecords();

        foreach ($records as $record) {
            $file_sep = explode(", ", $record->getField('Image Filenames'));
            $image_path = $record->getField('Path To Images');

            $num = count($file_sep);

            for ($c = 0; $c < $num; $c++) {
                if (strpos($file_sep[$c], '.jpg') !== false) {
                    $obj = new OrganismImage();
                    $obj->filename = $file_sep[$c];
                    $obj->filepath = $organism_images_root . $image_path;
                    array_push($organism_images, $obj);
                }
            }
        }
    } catch (FileMakerException $e) {
        echo 'An error occured ' . $e->getMessage() . ' - Code : ' . $e->getCode();
    }

    usort($organism_images, function ($a, $b) {
        return strcmp($a->filename, $b->filename);
    });

    return $organism_images;
}
