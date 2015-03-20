function requestLiveData() {
    $.ajax({
        url: 'data_live.php',
        dataType: 'json',
        success: function(jsonData) {
        
			var interval = 1000;
			var shiftMax = 60000 / interval;
            var series = chart.series[0],
                shift = series.data.length > shiftMax; // shift if the series is longer than shiftMax
            
            //set title
            chart.setTitle({ text: jsonData.title});
            
            // add the point
            var x = (new Date()).getTime();
            var y = jsonData.p1_current_power_in*1000; //kW -> W
            
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
    
    // Live chart
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
});