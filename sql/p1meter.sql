CREATE TABLE IF NOT EXISTS consumption (
	id bigint unsigned UNIQUE AUTO_INCREMENT,
    `inserted` timestamp NOT NULL UNIQUE,   
    ts datetime NOT NULL UNIQUE,     
	meter_low DECIMAL(10,3) unsigned NOT NULL,
	meter_normal DECIMAL(10,3) unsigned NOT NULL,
	current_power DECIMAL(10,3) unsigned NOT NULL,
    amp int(11) unsigned NOT NULL,
    rate_type_id tinyint(1) unsigned NOT NULL,     
KEY `rate_type_id` (`rate_type_id`)    
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS rate_types (
	rate_type_id tinyint(1) unsigned UNIQUE AUTO_INCREMENT,
	name varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

INSERT INTO rate_types VALUES (DEFAULT, "both");
INSERT INTO rate_types VALUES (DEFAULT, "low");
INSERT INTO rate_types VALUES (DEFAULT, "normal");


CREATE VIEW usage_per_day AS
SELECT 
    DATE(ts) as date, 
    (MAX(meter_normal)-MIN(meter_normal)) as e_normal, 
    (MAX(meter_low)-MIN(meter_low)) as e_low, 
    ((MAX(meter_normal)-MIN(meter_normal))+(MAX(meter_low)-MIN(meter_low))) as e_total, 
    MIN(`current_power`) as min_power, 
    MAX(`current_power`) as max_power, 
    AVG(`current_power`) as avg_power 
FROM consumption 
GROUP BY DATE(ts);

CREATE VIEW usage_per_hour_per_day AS
SELECT 
    ts as date, 
    HOUR(ts) as hour, 
    (MAX(meter_normal)-MIN(meter_normal)) as e_normal, 
    (MAX(meter_low)-MIN(meter_low)) as e_low, 
    ((MAX(meter_normal)-MIN(meter_normal))+(MAX(meter_low)-MIN(meter_low))) as e_total 
FROM consumption 
GROUP BY DATE(ts), HOUR(ts);

CREATE VIEW total_per_day_per_week AS
SELECT 
    date(`date`) as date, 
    day(`date`) as day, 
    week(`date`,3) as week, 
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY month(`date`), dayofmonth(`date`), week(`date`,3), year(`date`);

CREATE VIEW total_per_week AS
SELECT 
    week(`date`,3) as week, 
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY week(`date`,3), year(`date`);

CREATE VIEW total_per_day_per_month AS
SELECT 
    date(`date`) as date, 
    day(`date`) as day, 
    month(`date`) as month, 
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY dayofmonth(`date`), month(`date`), year(`date`);

CREATE VIEW total_per_month AS
SELECT 
    monthname(`date`) as monthname, 
    month(`date`) as month,
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY month(`usage_per_day`.`date`), year(`date`);

CREATE VIEW total_per_year AS
SELECT 
    year(`date`) as year, 
    sum(`e_normal`) as e_normal,
    sum(`e_low`) as e_low,
    sum(`e_total`) as e_total 
FROM `usage_per_day` 
GROUP BY year(`date`)