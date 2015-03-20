# usage_per_day + counter
SELECT 
    DATE(ts) as date,
    (MAX(meter_normal)-MIN(meter_normal)) as e_normal, 
    (MAX(meter_low)-MIN(meter_low)) as e_low, 
    ((MAX(meter_normal)-MIN(meter_normal))+(MAX(meter_low)-MIN(meter_low))) as e_total, 
    MIN(`current_power`) as min_power, MAX(`current_power`) as max_power 
    AVG(`current_power`) as avg_power,
    MIN(meter_low) as meter_low_start,
    MAX(meter_low) as meter_low_end, 
    MIN(meter_normal) as meter_normal_start,
    MAX(meter_normal) as meter_normal_end  
FROM consumption 
GROUP BY DATE(ts);

# top 10 common
SELECT DATE(ts) as date,`current_power`, COUNT(`current_power`) AS common_low 
FROM consumption
GROUP BY day(ts),`current_power`
ORDER BY COUNT(`current_power`) DESC limit 10

quarter
SELECT 
    monthname(`date`) as monthname,
	quarter(`date`) as quarter,
    month(`date`) as month,
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY monthname(`date`), quarter(`date`), year(`date`);
