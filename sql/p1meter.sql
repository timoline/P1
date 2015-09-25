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