$(document).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    }); 
    
    var options = {
        chart: {
            renderTo: 'container',
            type: 'spline',
            zoomType: 'x'
        },
        credits:{enabled:false},
        title: {text: ''},
        scrollbar:{
            enabled: true
        },        
        yAxis: [{
            labels:{
                    
            },        
            title: {
                text: 'Power'
            },
            min: 0,
            opposite: false       
        },
        {
            labels:{
                align:'left',
                x:10
            },        
            title: {
                text: 'Energy'
            },
            min: 0,            
            opposite: true
        }],        
        xAxis: {
           // categories: [],
            type: 'datetime',            
            tickWidth: 1,
            tickmarkPlacement: 'on',
            //minTickInterval: 0,
           //tickInterval: 0.6,
            labels: {
                formatter: function() {
                    return Highcharts.dateFormat('%H %M', this.value);
                },
                //step: 60
            }          
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
            valueSuffix: ' Watt',
            crosshairs: [{
                width: 1,
                dashStyle: 'solid',
                color: '#eeeeee'
            }]         
        },    
        legend: {
             enabled: true
        },
                
        series: [{}]
    }
   
    function createChart(json){    
			$.ajax({
				url: json,
				dataType: 'json',
				success: function( jsonData ) {
                    options.xAxis.categories = jsonData[0]['data'];
                    options.title.text = jsonData[3]['data'];   
                    
                    options.series[0] = jsonData[1];   
                    //options.series[0].yAxis = 1;                        
                    options.series[0].type = "areaspline";
                    options.series[0].tooltip = { valueSuffix: " watt" };
                    options.series[0].zIndex = 2; 

                    options.series[1] = jsonData[2];  
                    options.series[1].yAxis = 1;                    
                    options.series[1].type = "areaspline";
                    options.series[1].tooltip = { valueSuffix: " kWh" };
                    options.series[1].zIndex = 1; 

                    chart = new Highcharts.Chart(options);
                }
            });
    }   
    
    var jsonfile = "data_day.php";
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