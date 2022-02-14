<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <title><?php echo ucwords(basename(dirname(__FILE__))); ?></title>
  <meta name="description" content="" />
  <meta name="keywords" content="" />
  <?php
  $filedirect = basename(dirname(__FILE__));
  $suffex = substr($filedirect, -3);
  if ($suffex == "dae") {
    $path = '../../../';
  } elseif ($suffex == "nae") {
    $path = '../../../../';
  } elseif ($suffex !== "nae" or "dae") {
    $path = '../../../../../';
  }
  echo '<script src="' . $path . 'js/jquery.min.js"></script>';
  echo '<script src="' . $path . 'js/skel.min.js"></script>';
  echo '<script src="' . $path . 'js/skel-layers.min.js"></script>';
  echo '<script src="' . $path . 'js/init.js"></script>';
  echo '<script src="' . $path . 'js/scroll.js"></script>';
  ?>

  <noscript>
    <link rel="stylesheet" href="css/skelgallery.css" />
    <link rel="stylesheet" href="css/style.css" />
    <link rel="stylesheet" href="css/style-xlarge.css" />
  </noscript>

</head>

<body id="top">

  <!-- Header -->
  <header id="header" class="skel-layers-fixed">
    <h1><?php echo basename(dirname(__FILE__)); ?></h1>
    <nav id="nav">
      <ul>
        <?php
        include $path . 'php/header.php';
        ?>
      </ul>
    </nav>
  </header>

  <!-- Main -->
  <section id="main" class="wrapper style1">
    <header class="major">
      <?php
      if ($suffex == "dae") {
        $order = basename(dirname(__DIR__));
        $family = basename(dirname(__FILE__));
        echo '<h3><a href="../">' . $order . '</a></h3>';
        echo '<h2>' . $family . '</h2>';
      } elseif ($suffex == "nae") {
        $order = basename(dirname(dirname(__DIR__)));
        $family = basename(dirname(__DIR__));
        $subfamily = basename(dirname(__FILE__));
        echo '<h4><a href="../../">' . $order . '</a></h4>';
        echo '<h3><a href="../">' . $family . '</a></h3>';
        echo '<h2>' . $subfamily . '</h2>';
      } elseif ($suffex !== "nae" or "dae") {
        $order = basename(dirname(dirname(dirname(__DIR__))));
        $family = basename(dirname(dirname(__DIR__)));
        $subfamily = basename(dirname(__DIR__));
        $genus = basename(dirname(__FILE__));
        echo '<h5><a href="../../../">' . $order . '</a></h5>';
        echo '<h4><a href="../../">' . $family . '</a></h4>';
        echo '<h3><a href="../">' . $subfamily . '</a></h3>';
        echo '<h2>' . $genus . '</h2>';
      }

      if (file_exists('index-gen.php') and file_exists('id-index-l.php') !== 1 and file_exists('id-index-d.php')) {
        echo '<div class="pageheader"><a href="index-gen.php">View Genera Gallery</a>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<a href="id-index-d.php">View Dorsal Gallery</a></div>';
      } elseif (file_exists('index-gen.php') and file_exists('id-index-l.php') and file_exists('id-index-d.php') !== 1) {
        echo '<div class="pageheader"><a href="index-gen.php">View Genera Gallery</a>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<a href="id-index-l.php">View Lateral Gallery</a></div>';
      } elseif (file_exists('index-gen.php') and file_exists('id-index-l.php') !== 1 and file_exists('id-index-d.php') !== 1) {
        echo '<div class="pageheader"><a href="index-gen.php">View Genera Gallery</a></div>';
      } elseif (file_exists('index-gen.php') !== 1 and file_exists('id-index-l.php') !== 1 and file_exists('id-index-d.php')) {
        echo '<div class="pageheader"><a href="id-index-d.php">View Dorsal Gallery</a></div>';
      } elseif (file_exists('index-gen.php') !== 1 and file_exists('id-index-l.php') and file_exists('id-index-d.php') !== 1) {
        echo '<div class="pageheader"><a href="id-index-l.php">View Lateral Gallery</a></div>';
      }



      echo '</header>';

      /* Gallery Set-up */
      echo '<div class="container-fluid">';
      if ($suffex == "nae") {
        echo '<hr class="major" style="margin: 5em 0 5em 0" />';
      } else {
        echo '<hr class="major" />';
      }

      /*	<!-- Species Start --> */
      session_start();
      $organism_images_root  = '../../../organism_images/';
      $_SESSION['genusname'] = "";
      $prevname  = 'start';
      $lastmap = 'nomaphere';
      $prevmap = '';

      # Read csv - Sassan & Yuxin - Main/Blattodea/Archotermopsidae
      $filenames = array();
      $image_paths = array();

      if (($handle = fopen("../../../db.csv", "r")) !== FALSE) {
        fgetcsv($handle);
        while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
          $num_cols = count($data);
          if ($num_cols > 27) {
            if ($data[52] == $order && $data[23] == $family) {
              $file_sep = explode(", ", $data[28]);
              $image_path = $data[53];

              $num = count($file_sep);

              for ($c = 0; $c < $num; $c++) {
                if (strpos($file_sep[$c], '.jpg') !== false) {
                  array_push($filenames, $file_sep[$c]);
                  array_push($image_paths, $organism_images_root . $image_path);
                }
              }
            }
          }
        }
        fclose($handle);
      }

      sort($filenames, SORT_STRING);

      $dir = '.';
      $files = scandir($dir);
      $i = 0;
      foreach ($filenames as $entry) {

        $entryext = pathinfo($entry, PATHINFO_EXTENSION);

        if ($entry != "." && $entry != ".."  && $entryext == "jpg") {

          $chunks = explode(" (", $entry);
          $name = $chunks[0];
          $badwords = array(' female', ' male', ' Form A', ' Form B', ' Form C', ' Form E', ' Form F', ' form A', ' form B', ' form C', ' form E', ' form F', ' queen', ' worker', ' drone', ' exuvium', ' Paratype');
          $replace = '';
          $filespecies = str_replace($badwords, $replace, $name);

          $dataname = str_replace(" ", "-", $filespecies);
          $filespecies = str_replace("sp.", "sp", $filespecies);
          $mapfilename = $filespecies . '.php';



          if ($name != $prevname && $prevname !== "start") {
            echo '</div>';
            echo '</div>';
            if (file_exists($prevmap)) {
              echo '<section class="specimen"><h5><a href="' . $prevmap . '">View Specimen Records</a></h5></section>';
            }
            echo '<div class="speciesentry" id="' . $dataname . '">';
            echo '<section class="species">' . $name . '</section>';
            echo '<div class="row collapse-at-2" style="padding-left: 4.5%">';
          } elseif ($name != $prevname && $prevname == "start") {
            echo '<div class="speciesentry" id="' . $dataname . '">';
            echo '<section class="species">' . $name . '</section>';
            echo '<div class="row collapse-at-2" style="padding-left: 4.5%">';
          }

          echo '<div class="span6">';
          echo '	<section class="gallery">';
          #echo '<section class="image_path">' . $image_paths[$i] . $entry . '</section>';
          echo '		<a href="' . $image_paths[$i] . $entry . '" class="image fit"><img src="' . $image_paths[$i] . $entry . '" alt="" /></a>';
          echo '	</section>';
          echo ' </div>';

          $prevname = $name;
          $prevmap = $mapfilename;
          $lastmap = $mapfilename;
        }
        $i++;
      }

      echo '</div>';
      echo '</div>';
      if (file_exists($lastmap)) {
        echo '<section class="specimen"><h5><a href="' . $lastmap . '">View Specimen Records</a></h5></section>';
      }


      ?>
      <!-- Species End -->

  </section>

  <!-- Footer -->
  <?php
  include $path . 'php/footer.php'
  ?>
</body>

</html>