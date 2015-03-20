<?php

class Database {

    private $_db = null;

    /**
     * Constructor, makes a database connection
     */
    public function __construct($config) {

        try {
            $this->_db = new PDO('mysql:host='.$config['db_host'].';dbname='.$config['db_name'], $config['db_user'], $config['db_pass'], array( 
      			PDO::MYSQL_ATTR_USE_BUFFERED_QUERY => true
   			));
            $this->_db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->_db->query('SET CHARACTER SET utf8');
        } catch (PDOException $e) {
            exit('Error while connecting to database.'.$e->getMessage());
        }
    }

    private function printErrorMessage($message) {
        echo $message;
    }

  
	
   /**
    * Add minute data (cronjob)
    */ 
    public function addMinuteData($ts, $meter_low, $meter_normal, $current_power, $amp, $rate_type_id) {

        try {
            $sth = $this->_db->prepare("INSERT INTO `consumption` (
            	ts,
				meter_low,
				meter_normal,
				current_power,
				amp,
                rate_type_id
            ) VALUES (
            	:ts,
				:meter_low,
				:meter_normal,
				:current_power,
				:amp,
                :rate_type_id
            ) 
	    ON DUPLICATE KEY UPDATE meter_normal = :meter_normal, meter_low = :meter_low, current_power = :current_power, amp = :amp, rate_type_id = :rate_type_id");

            $sth->bindValue(':ts', $ts, PDO::PARAM_STR);
			$sth->bindValue(':meter_low', $meter_low, PDO::PARAM_INT);
			$sth->bindValue(':meter_normal', $meter_normal, PDO::PARAM_INT);
			$sth->bindValue(':current_power', $current_power, PDO::PARAM_INT);
			$sth->bindValue(':amp', $amp, PDO::PARAM_INT);
            $sth->bindValue(':rate_type_id', $rate_type_id, PDO::PARAM_INT);
			
            $sth->execute();
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    } 
	
  
   /**
    * Add missing minute data (cronjob)
    */ 
    public function addMissingMinuteData($ts) {

        try {
            $sth = $this->_db->prepare("INSERT INTO `consumption` (
				ts,
				meter_low,
				meter_normal,
				current_power,
				amp,
                rate_type_id
            ) select :ts,
				'0',
				'0',
				'0',
                '0',
				'3'
              from dual where exists (select * from consumption where ts <  :ts);
	    ");

            $sth->bindValue(':ts', $ts, PDO::PARAM_STR);
            $sth->execute();
        } catch (PDOException $e) {
        }
    } 

    
 	/**
	* Get usage per day (min,max,avg)
	*/
    public function getUsageDay($date) {
        try {
            $sth = $this->_db->prepare("
            SELECT 
                * 
            FROM 
            `usage_per_day`
            WHERE
                DATE(date) = :date");

            $sth->bindValue(':date', $date, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }     
 
 
	/**
	* Get usage day per minute //getMinuteDay
	*/
    public function getMinuteDay($date) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`consumption`
            WHERE
                DATE(ts) = :date");

            $sth->bindValue(':date', $date, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    } 
 
 
	/**
	* Get usage_per_day_per_hour //getHourDay
	*/
    public function getHourDay($date) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`usage_per_hour_per_day`
            WHERE
                DATE(date) = :date");

            $sth->bindValue(':date', $date, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }  
 
 
 	/**
	* Get total_per_day_per_week //getDayWeek
	*/
    public function getDayWeek($week,$year) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`total_per_day_per_week`
            WHERE
                week = :week
            AND
                year = :year");                

            $sth->bindValue(':week', $week, PDO::PARAM_STR); 
            $sth->bindValue(':year', $year, PDO::PARAM_STR);             
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }  	     
 
 
 	/**
	* Get total_per_week //getWeekYear
	*/
    public function getWeekYear($week,$year) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`total_per_week`
            WHERE
                year = :year
            AND    
                week = :week");

            $sth->bindValue(':week', $week, PDO::PARAM_STR);                 
            $sth->bindValue(':year', $year, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }   

    
	/**
	* Get total_per_day_per_month //getDayMonth
	*/
    public function getDayMonth($month,$year) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`total_per_day_per_month`
            WHERE
                month = :month
            AND
                year = :year");

            $sth->bindValue(':month', $month, PDO::PARAM_STR); 
            $sth->bindValue(':year', $year, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }  	     

    
	/**
	* Get total_per_month //getMonthYear
	*/
    public function getMonthYear($month = null,$year) {
        try {
            if($month = null)
            {
                $sth = $this->_db->prepare("
                SELECT
                    *
                FROM 
                    `total_per_month`
                WHERE
                    year = :year
                AND    
                    month = :month");

                $sth->bindValue(':month', $month, PDO::PARAM_STR); 
                $sth->bindValue(':year', $year, PDO::PARAM_STR); 
                $sth->execute();

                $rows = $sth->fetchAll(PDO::FETCH_OBJ);
                return $rows;
            }
            else
            {
                  $sth = $this->_db->prepare("
                SELECT
                    *
                FROM 
                    `total_per_month`
                WHERE
                    year = :year");

                $sth->bindValue(':year', $year, PDO::PARAM_STR); 
                $sth->execute();

                $rows = $sth->fetchAll(PDO::FETCH_OBJ);
                return $rows;          
            }
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }  	  
  
  
	/**
	* Get total_per_year //getYears
	*/
    public function getYears($year) {
        try {
            $sth = $this->_db->prepare("
            SELECT
            	*
            FROM 
            	`total_per_year`
            WHERE
                year = :year");

            $sth->bindValue(':year', $year, PDO::PARAM_STR); 
            $sth->execute();

            $rows = $sth->fetchAll(PDO::FETCH_OBJ);
			return $rows;
        } catch (PDOException $e) {
            $this->printErrorMessage($e->getMessage());
        }
    }  	   

  
}