var tmpWatt = 0;
$(document).ready(function() {

    function updateDash(){
        $.ajax({
            url: "data_dashboard.php",
            dataType: "json",
            cache: false,
            success: function(json) {
            //console.log(json)
                var currentpowerin = json.p1_current_power_in*1000; // kW -> W
                
                if(tmpWatt < parseInt(currentpowerin)){
                    updown = "countUp";
                    $('#p1_current_power_in').html("<span class='"+updown+"'>"+(currentpowerin)+"</span>"); 
                    $("#p1_current_power_in").effect( "highlight",{color:"#FF0000"}, 1000 );
                }
                else if(tmpWatt== parseInt(currentpowerin)){
                    updown = "";
                    $('#p1_current_power_in').html("<span class='"+updown+"'>"+(currentpowerin)+"</span>"); 
                }
                else
                {
                    updown = "countDown";
                    $('#p1_current_power_in').html("<span class='"+updown+"'>"+(currentpowerin)+"</span>");  
                    $("#p1_current_power_in").effect( "highlight",{color:"#008000"}, 1000 ); //2C3539
                }
                tmpWatt = parseInt(currentpowerin);
                
                //low - normal tariff
                var currenttariff = json.p1_current_tariff;
                if (currenttariff == 1 ) {
                    rate = "Low";
                }
                else {
                    rate = "Normal";
                }                
                
                //smartmeter
                $('#p1_timestamp').html(json.p1_timestamp);  
                $('#p1_meter_supplier').html(json.p1_meter_supplier);               
                $('#p1_dsmr_version').html(json.p1_dsmr_version);
                $('#p1_powerfailures').html(json.p1_powerfailures);
                
                //counter
                $('#p1_current_tariff').html(rate);                
                $('#p1_meterreading_in_1').html(json.p1_meterreading_in_1); //kWh
                $('#p1_meterreading_in_2').html(json.p1_meterreading_in_2); //kWh 
                    
                //usage
                $('#p1_instantaneous_current_l1').html(json.p1_instantaneous_current_l1); //A              

                $('#today_min_power').html(json.today_min_power);
                $('#today_max_power').html(json.today_max_power);
                $('#today_avg_power').html(json.today_avg_power);

                //today
                $('#today_date').html(json.today_date);
                $('#today_normal').html(json.today_normal);
                $('#today_low').html(json.today_low);
                $('#today_total').html(json.today_total);    
                
                //week
                $('#week_date').html(json.week_date);
                $('#week_normal').html(json.week_normal);
                $('#week_low').html(json.week_low);
                $('#week_total').html(json.week_total);     

                //month
                $('#month_date').html(json.month_date);
                $('#month_normal').html(json.month_normal);
                $('#month_low').html(json.month_low);
                $('#month_total').html(json.month_total);    

                //year
                $('#year_date').html(json.year_date);
                $('#year_normal').html(json.year_normal);
                $('#year_low').html(json.year_low);
                $('#year_total').html(json.year_total);       
				
            }             
        });              
    }
    updateDash();
    setInterval(updateDash, 5000);
});