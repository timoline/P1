
    // Create the chart
function createChart(json){      
    $.ajax({
        url: json,
        dataType: 'json',
        success: function( jsonData ) {

            Highcharts.setOptions({
                global: {
                    useUTC: false
                }
            }); 


            // get date from first json object for using in the title
            var chartTitle = $.datepicker.formatDate( "DD d MM yy",new Date(jsonData[0][0]));
            
            window.chart = new Highcharts.StockChart({
                chart : {
                    renderTo : 'container',
                    type: 'areaspline',
                    zoomType: 'x'
                },
                credits:{enabled:false},
                title: {text: chartTitle},
                exporting: {enabled: false},
                yAxis : {
                    labels:{
                        align:'left',
                        x:10
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
                    valueSuffix: ' Watt',
                    crosshairs: [{
                        width: 1,
                        dashStyle: 'solid',
                        color: '#eeeeee'
                    }],
                },  
                navigator: {
                    enabled: true,
                    height: 60,
                    maskFill: 'rgba(180, 198, 220, 0.1)'
                },        
                rangeSelector: {
                    enabled: false
                },        
                series : [{
                    name : 'Power usage',
                    data : jsonData
                }]
            });
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
