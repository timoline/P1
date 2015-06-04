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
$a = 0;
$series1 = array();
$series1['name'] = 'Power';

$series2 = array();
$series2['name'] = 'Energy';

$series3 = array();
$series3['name'] = 'Title';
$series3['data'] = date('l j F Y', strtotime($date));
    
foreach ($rows as $r){
    $category['data'][] = strtotime($r->ts)*1000;
    $series1['data'][] = ($r->current_power)*1000; // kW => Watt
    $a = $a + round(($r->current_power*60)/3.6) ;
    $series2['data'][] = $a;    //???	
}
    $result = array();
    array_push($result,$category);
    array_push($result,$series1);
    array_push($result,$series2);    
    array_push($result,$series3);    
//$result["date"] = "2015-03-26";
/* output in required format */
header('Content-type: application/json');
echo json_encode($result, JSON_NUMERIC_CHECK);
?>