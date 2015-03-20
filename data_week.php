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

//this week
$date = $today;

$week = (int)date('W', strtotime($date)); 
$year = (int)date('Y', strtotime($date)); 
//$date = date('W',strtotime("-1 week"));
//var_dump($date);
$rows = $db->getDayWeek($week,$year);
if(count($rows) == 0)
{
    $category = array();
    $category['name'] = 'day';
    $category['data'] = strtotime($date) *1000;

    $series1 = array();
    $series1['name'] = 'Low rate';
    $series1['data'] = 0;

    $series2 = array();
    $series2['name'] = 'Normal rate';
    $series2['data'] = 0;

    $series3 = array();
    $series3['name'] = 'Title';
    $series3['data'] = "No data available"; 

    $result = array();
    array_push($result,$category);
    array_push($result,$series1);
    array_push($result,$series2);
    array_push($result,$series3);
}
else
{
    $category = array();
    $category['name'] = 'day';

    $series1 = array();
    $series1['name'] = 'Low rate';

    $series2 = array();
    $series2['name'] = 'Normal rate';

    $series3 = array();
    $series3['name'] = 'Title';
    $series3['data'] = "Week ".$week." of ".$year;

    foreach ($rows as $r){
        $category['data'][] = strtotime($r->date)*1000;
        $series1['data'][] = $r->e_low;
        $series2['data'][] = $r->e_normal;
    }

    $result = array();
    array_push($result,$category);
    array_push($result,$series1);
    array_push($result,$series2);
    array_push($result,$series3);
}

/* output in required format */
header('Content-type: application/json');
echo json_encode($result, JSON_NUMERIC_CHECK);
?>