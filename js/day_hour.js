$(document).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    }); 
            
    var options = {
        chart: {
            renderTo: 'container',
            type: 'column',
            zoomType: 'x'
        },
        credits:{enabled:false},
        title: {text: ''},
        xAxis: {
            categories: [],
            tickWidth: 1,
            tickmarkPlacement: 'on',
            type: 'datetime',            
            labels: {
                formatter: function() {
                    return Highcharts.dateFormat('%H', this.value);
                }
            }            
        },
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
        tooltip: {
            shared: true,
            useHTML: true,
            backgroundColor: '#FFFFFF',
            borderColor: '#EEEEEE',
            xDateFormat: '%H:%M',      
            headerFormat: '<div class="chart_tooltip_header">{point.key}</div><table class="chart_tooltip_table"><thead><tr><th>Consumption</th></tr></thead>',
            pointFormat: '<tbody><tr><td class="chart_tooltip_name" style="color: {series.color}">\u25A0 {series.name}: </td>' +
                         '<td class="chart_tooltip_value">{point.y}</td></tr>',
            footerFormat: '</tbody></table>',
            valueSuffix: ' kWh',
            crosshairs: [{
                width: 1,
                dashStyle: 'solid',
                color: '#eeeeee'
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
                            
                        }
                    }
                }
            }
        },                  
        series: []
    }
    
    function createChart(json){    
			$.ajax({
				url: json,
				dataType: 'json',
				success: function( jsonData ) {
                    options.xAxis.categories = jsonData[0]['data'];
                    options.series[0] = jsonData[1];
                    options.series[1] = jsonData[2];
                    options.title.text = jsonData[3]['data'];        
                    
                    chart = new Highcharts.Chart(options);
                }
            });
    }    
 
    var jsonfile = "data_day_hour.php";
    createChart(jsonfile);
     
    var now = new Date();   
    var today = new Date();

    $('#prev').click(function(){  
            now.setDate(now.getDate() - 1);
            date = $.datepicker.formatDate( "yy-mm-d",new Date(now))
            createChart(jsonfile+"?date="+date);
    });
    
    $('#next').click(function(){
        if(now < today){
            now.setDate(now.getDate() + 1);
            date = $.datepicker.formatDate( "yy-mm-d",new Date(now))
            createChart(jsonfile+"?date="+date);
        }    
    });    
    

});