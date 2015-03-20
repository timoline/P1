<?php
include "inc/settings.inc.php";
include "classes/database.class.php";

$db = new Database($config);

$json_file = file_get_contents($config['p1datajsonurl']);
$json_results = json_decode($json_file, true);

$date = date('Y-m-d');
$today = $date;
$week = (int)date('W', strtotime($date)); 
$month = (int)date('m', strtotime($date)); 
$year = (int)date('Y', strtotime($date)); 

$today_rows = $db->getUsageDay($today);
$week_rows = $db->getWeekYear($week,$year);
$month_rows = $db->getMonthYear($month,$year);
$year_rows = $db->getYears($year);

//var_dump($week_rows);
foreach ($today_rows as $tr){
    $today_results['today_date'] = ($tr->date); 
    $today_results['today_normal'] = ($tr->e_normal); 
    $today_results['today_low'] = ($tr->e_low); 
    $today_results['today_total'] = ($tr->e_total); 
    $today_results['today_min_power'] = ($tr->min_power)*1000; //kw ->W
    $today_results['today_max_power'] = ($tr->max_power)*1000; //kw ->W
    $today_results['today_avg_power'] = ($tr->avg_power)*1000; //kw ->W
}

foreach ($week_rows as $wr){
    $week_results['week_date'] = ($wr->week); 
    $week_results['week_normal'] = ($wr->e_normal); 
    $week_results['week_low'] = ($wr->e_low); 
    $week_results['week_total'] = ($wr->e_total); 
}

foreach ($month_rows as $mr){
    $month_results['month_date'] = ($mr->monthname); 
    $month_results['month_normal'] = ($mr->e_normal); 
    $month_results['month_low'] = ($mr->e_low); 
    $month_results['month_total'] = ($mr->e_total); 
}

foreach ($year_rows as $yr){
    $year_results['year_date'] = ($yr->year); 
    $year_results['year_normal'] = ($yr->e_normal); 
    $year_results['year_low'] = ($yr->e_low); 
    $year_results['year_total'] = ($yr->e_total); 
}

$results = array_merge($json_results, $today_results, $week_results, $month_results, $year_results);

header('Content-type: application/json');
echo json_encode($results , JSON_NUMERIC_CHECK);

/*
if ($json_results){
    // output in required format 
    header('Content-type: application/json');
    echo json_encode($json_results , JSON_NUMERIC_CHECK);
}   
*/ 
?>