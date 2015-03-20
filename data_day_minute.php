<?php
include "inc/settings.inc.php";
include "classes/database.class.php";

$db = new Database($config);

if(isset($_GET['date']))
{
    $today = $_GET['date'];
}
else
{
    $today = date('Y-m-d');
}
//today
$date = $today;

$rows = $db->getMinuteDay($date);

foreach ($rows as $r){
    $datetime = strtotime($r->ts)*1000;
    $series1 = ($r->current_power)*1000; // kW => Watt
    $result[]= array($datetime,$series1); 
}

//$result["date"] = "2015-03-26";
/* output in required format */
header('Content-type: application/json');
echo json_encode($result, JSON_NUMERIC_CHECK);
?>