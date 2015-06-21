function requestLiveData() {
    $.ajax({
        url: 'data_live.php',
        dataType: 'json',
        success: function(json) {
        
			var interval = 1000;
			var shiftMax = 60000 / interval;
            var series = chart.series[0],
                shift = series.data.length > shiftMax; // shift if the series is longer than shiftMax
            
            //set title
            chart.setTitle({ text: json.title});
            
            // add the point
            var x = (new Date()).getTime();
            var y = json.p1_current_power_in*1000; //kW -> W
            
            chart.series[0].addPoint([x, y], true, shift);                  
            
            // call it again after one second
            setTimeout(requestLiveData, interval);    
        },
        cache: false
    });
}

$(document).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    }); 
    
    var options = {
        chart: {
            renderTo: 'history',
            type: 'column',
            zoomType: 'x'
        },
        credits:{enabled:false},
        title: {text: ''},
        yAxis: {
            labels:{
                align:'left',
                x:10
            },        
            title: {
                text: ''
            },
            opposite: true
        },        
        xAxis: {
            categories: [],
            tickWidth: 1,
            tickmarkPlacement: 'on',
            type: 'datetime',
            labels: {
                formatter: function() {
                    return Highcharts.dateFormat('%e', this.value);
                }
            }          
        },
        tooltip: {
            shared: true,
            useHTML: true,
            backgroundColor: '#FFFFFF',
            borderColor: '#EEEEEE',
            xDateFormat: '%A %e %B %Y',
            headerFormat: '<div class="chart_tooltip_header">{point.key}</div><table class="chart_tooltip_table"><thead><tr><th>Consumption</th></tr></thead>',
            pointFormat: '<tbody><tr><td class="chart_tooltip_name" style="color: {series.color}">\u25A0 {series.name}: </td>' +
                         '<td class="chart_tooltip_value">{point.y}</td></tr>',
            footerFormat: '<td colspan="2" class="chart_tooltip_total"><b>{point.total} kWh</b></td></tbody></table>',
            //valueSuffix: ' kWh',
            crosshairs: [{
                dashStyle: 'solid',
                color: '#EEEEEE'
            }]         
        },    
        legend: {
            borderWidth: 0
        },
        plotOptions: {
            column: {
                stacking: 'normal'
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function () {
							var dt = this.category;
							var chart_type =  $('#history').data('chart'); 

							switch (chart_type) {

							case 'year': 
								var target = "month";
								break;
							case 'month':
								var target = "day_hour";
								break;
							case 'week':
								var target = "day_hour";
								break;
							default:
								var target = "day";
								break;
							} 								
							
							date = $.datepicker.formatDate( "yy-mm-dd",new Date(dt));
							
							$('#datepicker').datepicker('setDate',date);
							$('#history').data('chart', target);	
							$('#chart_panelheader').html(target);
													
							$('.showChart').removeClass('active');	
							$('.showChart').blur();							
							$('[data-chart='+target+']').addClass('active');	

							createChart(target,date);									
                        }
                    }
                }
            }
        },                  
        series: []
    }
 
	//create the chart
    function createChart(target,date){    
			$.ajax({
				url: 'data_'+target+'.php?date='+date,
				dataType: 'json',
				success: function( jsonData ) {
	
				//console.log(jsonData);
                    options.xAxis.categories = jsonData[0]['data'];
                    options.series[0] = jsonData[1];
                    options.series[1] = jsonData[2];
                    options.title.text = jsonData[3]['data'];   
					options.series[0].zIndex = 1;	
					options.series[1].tooltip = { valueSuffix: " kWh" };					

					switch (target) {

					case 'day': 
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%H %M', this.value);}}
						options.series[0].tooltip = { valueSuffix: " watt", xDateFormat: '%H:%M', footerFormat:''};	
						options.series[0].type = "areaspline";
						options.series[1].type = "areaspline";
						options.series[1].zIndex = 0;
						break;
					case 'day_hour':
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%H', this.value);}}
						options.series[0].tooltip = { valueSuffix: " kWh", xDateFormat: '%H:%M', footerFormat:''};	
						break;
					case 'week':
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%e', this.value);}}	
						options.series[0].tooltip = { valueSuffix: " kWh", xDateFormat: '%A %e %B %Y' };	
					   break;
					case 'month':
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%e', this.value);}}	
						options.series[0].tooltip = { valueSuffix: " kWh", xDateFormat: '%A %e %B %Y' };
						break;
					case 'year':
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%B', this.value);}}
						options.series[0].tooltip = { valueSuffix: " kWh", xDateFormat: '%B %Y' };	
						break;					   
					default:
						options.xAxis.labels = { formatter: function() { return Highcharts.dateFormat('%e', this.value);}}	
						options.series[0].tooltip = { valueSuffix: " kWh", xDateFormat: '%A %e %B %Y' };
						break;
					} 
		                       
                    historychart = new Highcharts.Chart(options);
                }
            });
    }   
    
	//first start
	var target = "month"; 
	var date= $('#datepicker').val();
	$('#live').hide();
	$('#history').data('chart', target);	
	$('#chart_panelheader').html(target);	
    createChart(target,date);
   
   /* 
	var target ="live";
	$('#history').hide();
	$('#history').data('chart', target);	
	$('#chart_panelheader').html(target);
    */	
								
   // Live chart   
	function createLiveChart(){     
		chart = new Highcharts.Chart({
			chart: {
				renderTo: 'live',
				zoomType: 'x',            
				defaultSeriesType: 'spline',
				events: {
					load: requestLiveData
				}
			},         
			credits: {
				enabled: false
			},
			legend: {
				enabled: false
			},		      
			//title: {text: title},
			yAxis: {
				labels:{
					align:'left',
					x:10
				},        
				title: {
					text: ''
				},
				opposite: true,        
				showFirstLabel: false
			},        
			xAxis: {
				type: 'datetime',
				tickPixelInterval: 150
			},
			tooltip: {
				shared: true,
				useHTML: true,
				backgroundColor: '#FFFFFF',
				borderColor: '#EEEEEE',
				xDateFormat: '%H:%M:%S', 
				headerFormat: '<div class="chart_tooltip_header">{point.key}</div><table class="chart_tooltip_table"><thead><tr><th>Consumption</th></tr></thead>',
				pointFormat: '<tbody><tr><td class="chart_tooltip_name" style="color: {series.color}">\u25A0 {series.name}: </td>' +
							 '<td class="chart_tooltip_value">{point.y}</td></tr>',
				footerFormat: '</tbody></table>',
				valueSuffix: ' Watt',            
				crosshairs: [{
					width: 1,
					dashStyle: 'solid',
					color: '#eeeeee'
				}]          
			},         
			series: [{
				name: 'Power usage',
				data: [],
				marker: {radius: 2}
			}],
			exporting: {
				enabled: false
			}		
		});  
	}

	// Show chart (navbar)
	$('.showChart').click(function(){
		var chart = $(this).data('chart');
		$('.chart').hide();
		$('.'+chart).show();
			
		$('.btn-group a').each(function(){
			$(this).removeClass('active');	
			$(this).blur();	
		});
		$(this).addClass('active');

		$('#history').data('chart', chart);
		$('#chart_panelheader').html(chart);
		if(chart == 'live')
		{
			createLiveChart();
		}	
		else
		{
			createChart(chart, $('#datepicker').val());
		}
		//console.log(chart);	
	});
	
	$('#prev').click(function () {
	   prev_next(-1);
	return false;
	});	

    $('#next').click(function () {
		prev_next(1);
	return false;
	});

	function prev_next(type) {
		var chart_type = $('#history').data('chart');
		//console.log(chart_type);    
		var $picker = $("#datepicker");                                                                              
		var date=new Date($picker.datepicker('getDate'));

		if (type!==1) type=-1;

		switch (chart_type) {
	
		case 'week': 
			date.setDate(date.getDate()+(7*type));
			break;
		case 'month':
			date.setMonth(date.getMonth()+(1*type));
			break;
		case 'year':
			date.setFullYear(date.getFullYear()+(1*type));
			break;
		default:
			date.setDate(date.getDate()+(1*type));
			break;
		} 
		$picker.datepicker('setDate', date);
		var target = $('#history').data('chart');                                                              

		date = $picker.datepicker({ dateFormat: 'yy-mm-dd' }).val();

		createChart(target, date);                                         
	   
	}

	// Datepicker
	$('#datepicker').datepicker({
		inline: true,
		dateFormat: 'yy-mm-dd',
		maxDate: new Date(),
		showOn: 'focus',
		changeMonth: true,
		changeYear: true,	
		firstDay: 1,
		showWeek: true,
		onSelect: function(date, inst){				
			var target = $('#history').data('chart');			
			createChart(target, date);
		}		
	});
  
});