$(document).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    }); 
    
    var options = {
        chart: {
            renderTo: 'container',
            type: 'areaspline',
            zoomType: 'x'
        },
        credits:{enabled:false},
        title: {text: ''},
        navigator: {
            enabled: true,
            height: 60,
            maskFill: 'rgba(180, 198, 220, 0.2)'
        },
        scrollbar:{
            enabled: true
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
             enabled: false
        },
                
        series: [{}]
    }
   
    function createChart(json){    
			$.ajax({
				url: json,
				dataType: 'json',
				success: function( jsonData ) {
                  //  options.xAxis.categories = jsonData[0]['data'];
                    options.series[0].data = jsonData;
                   // options.title.text = jsonData[2]['data'];        

                    chart = new Highcharts.Chart(options);
                }
            });
    }   
    
    var jsonfile = "data_day_minute.php";
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