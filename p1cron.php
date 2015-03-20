#!/usr/bin/php
<?php
if (PHP_SAPI == "cli")
{
	include "inc/settings.inc.php";
	include "classes/database.class.php";
	
	$db = new Database($config);
	
    $json_file = file_get_contents($config['p1datajsonurl']);
    $json_results = json_decode($json_file, true);
    if ($json_results)
    {
        $ts = $json_results["p1_timestamp"];
        $meter_low = $json_results["p1_meterreading_in_1"];
        $meter_normal = $json_results["p1_meterreading_in_2"];
        $current_power = $json_results["p1_current_power_in"];
        $amp = $json_results["p1_instantaneous_current_l1"];
        $rate = $json_results["p1_current_tariff"];
        
        $db->addMinuteData($ts, $meter_low, $meter_normal, $current_power, $amp, $rate);
        
        //echo $ts."\n";
    }
    
    /* missing minute data
    $time = time()-(86400*2);
    $nu = time();
    for ($i = $time; $i < $nu ;$i = $i + 60 ) {
        $db->addMissingMinuteData( date('Y-m-d H:i:00',$i));
    }
    */
		
	exit;	
}
else
{
	echo "No direct access allowed!";
}

?>