<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="" />
    <meta name="author" content="Timrz">
    <meta name="title" content="" />
    <meta name="keywords" content="" />
    <meta name="robot" content="INDEX,FOLLOW" />
    <meta name="revisit-after" content="1 days" />

    <title>Smartmeter</title>

    <!-- Bootstrap Core CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
	<link rel="stylesheet" href="css/jquery-bootstrap-datepicker.css">

    <!-- Custom Fonts -->


    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
        <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
        <script src="https://oss.maxcdn.com/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
</head>
<body>

<!-- Navigation -->
<nav class="navbar navbar-fixed-top" role="navigation">
    <div class="container-fluid">
        <!-- Brand and toggle get grouped for better mobile display -->
        <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-1">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="#">Smartmeter</a>
        </div>
        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse" id="navbar-1">
            <ul class="nav navbar-nav navbar-right">
				<li><a href="index.php">History</a></li>  
                <li><a href="dashboard.html">Dashboard</a></li>  
				<li><a href="insights.html">Insights</a></li>  
            </ul>
        </div>	
    </div>
    <!-- /.container -->
</nav>


<!-- Page Content -->
<div class="container-fluid">

    <!--  Toolbar -->
    <div class="row">

		<div class="col-xs-12 col-sm-12 col-lg-12">	
			<nav class="navbar navbar-default">
			<!--
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-collapse-1">
					<span class="sr-only">Toggle navigation</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>		
			 -->		
				<div id="datepickContainer" class="chart day day_hour week month year input-group pull-left">
					<input type="text" class="form-control" id="datepicker" value="<?php echo date("Y-m-d"); ?>">			
				</div>		 				
									
				<div class="btn-group pull-right" id="navbar-collapse-1">		
				
					<a role="button" id="today" href="#" class="btn btn-default navbar-btn">
						<span class="hidden-xs">Today</span>
						<span class="visible-xs">Td</span>
					</a>					
									
					<a role="button" href="#" data-chart="live" class="showChart btn btn-default navbar-btn">
						<span class="hidden-xs">Live</span>
						<span class="visible-xs">L</span>
					</a>
					<a role="button" href="#" data-chart="day" class="showChart btn btn-default navbar-btn">
						<span class="hidden-xs">Day</span>
						<span class="visible-xs">Dy</span>
					</a>
					<a role="button" href="#" data-chart="day_hour" class="showChart btn btn-default navbar-btn">
						<span class="hidden-xs">Day(hour)</span>
						<span class="visible-xs">Hr</span>
					</a>
					<a role="button" href="#" data-chart="week" class="showChart btn btn-default navbar-btn">
						<span class="hidden-xs">Week</span>
						<span class="visible-xs">Wk</span>
					</a>
					<a role="button" href="#" data-chart="month" class="showChart btn btn-default navbar-btn active">
						<span class="hidden-xs">Month</span>
						<span class="visible-xs">Mth</span>
					</a>
					<a role="button" href="#" data-chart="year" class="showChart btn btn-default navbar-btn">
						<span class="hidden-xs">Year</span>
						<span class="visible-xs">Yr</span>
					</a>
				</div>	
<!--			
				<div class="btn-group">		
					<a role="button" href="#" id="kwh" class="active btn btn-default navbar-btn">
						<span class="hidden-xs">kWh</span>
						<span class="visible-xs">kWh</span>
					</a>
					<a role="button" href="#" id="euro" class="btn btn-default navbar-btn">
						<span class="hidden-xs">€</span>
						<span class="visible-xs">€</span>
					</a>					
				</div>					
-->											
			</nav>
		</div>	
	</div>	
    
	<!--  Chart -->	
	<div class="row">	
         <div class="col-xs-12 col-sm-12 col-lg-12">
            <div class="panel panel-primary">
                <div class="panel-heading">
                    <div id="chart_panelheader">Chart</div>  
                    <div class="pull-left chartnavbutton"><button id="prev" type="button" class="btn btn-primary">&lsaquo;</button></div>  
                    <div class="pull-right chartnavbutton"><button id="next" type="button" class="btn btn-primary">&rsaquo;</button></div>  
                </div>
                <div class="panel-body">    				
                    <div id="history" class="chart day day_hour week month year"></div>                
					<div id="live" class="chart live"></div>
                </div>
            </div>
        </div> 
    <!-- /.row -->
    </div>
<!-- /.container -->
</div>
<!-- Footer -->
<footer class="footer">
    <div class="row">
        <div class="col-lg-12 copyright">
            <p>Copyright &copy; Timrz 2015</p>
        </div>
    </div>
</footer>
<!-- jQuery -->
<script type="text/javascript" src="http://code.jquery.com/jquery-1.11.3.js"></script>
<script type='text/javascript' src='http://code.jquery.com/ui/1.11.4/jquery-ui.js'></script>        
<script type="text/javascript" src="http://code.highcharts.com/highcharts.js"></script>
<!-- <script type="text/javascript" src="http://code.highcharts.com/modules/exporting.js"></script> -->

<!-- Bootstrap Core JavaScript -->
<script type='text/javascript' src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
<script type="text/javascript" src="js/script.js"></script>	

</body>
</html>
