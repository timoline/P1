<?php
include "inc/settings.inc.php";

$json_file = file_get_contents($config['p1datajsonurl']);
$json_results = json_decode($json_file, true);

$date = date('Y-m-d');
$today = $date;

$json_results['title'] = date('l j F Y', strtotime($date));

if ($json_results){

    // output in required format 
    header('Content-type: application/json');
    echo json_encode($json_results, JSON_NUMERIC_CHECK);
}    

?>