//var oldvalue= 0;
var oldjson = 0;

$(document).ready(function() {

	function highlightValue(key,value,oldvalue) {
		//console.log("NEW: "+value);
		//console.log("OLD: "+oldvalue);
		if(oldvalue < value){
			updown = "countUp";
			$('#'+key).html("<span class='"+updown+"'>"+(value)+"</span>"); 
			//$('#'+key).html(value); 
			$('#'+key).effect( "highlight",{color:"#FF0000"}, 1000 );
		}
		else if(oldvalue == value){
			updown = "";
			$('#'+key).html("<span class='"+updown+"'>"+(value)+"</span>"); 
			//$('#'+key).html(value); 
		}
		else
		{
			updown = "countDown";
			$('#'+key).html("<span class='"+updown+"'>"+(value)+"</span>");  
			//$('#'+key).html(value); 
			$('#'+key).effect( "highlight",{color:"#008000"}, 1000 ); //2C3539
		}		
		
	}

    function updateDash(){
        $.ajax({
            url: "data_dashboard.php",
            dataType: "json",
            cache: false,
            success: function(json) {
            //console.log(json)
//******************************************************************************************
				//convert: kW -> W	
				json["p1_current_power_in"] = (json["p1_current_power_in"])*1000;		
								
                //convert tariff: low - normal
                var currenttariff = json.p1_current_tariff;
                if (currenttariff == 1 ) {
                    json["p1_current_tariff"]  = "Low";
                }
                else {
                    json["p1_current_tariff"]  = "Normal";
                }  
//******************************************************************************************
				for (var key in json)
				{									
					var value = json[key];
					var oldvalue = oldjson[key];

					//$('#'+key).html(json[key]);  
					highlightValue(key,value,oldvalue); 
						
					//console.log($('#'+key).html(json[key]));
				}
				
				oldjson = json;	
				//console.log("oldjson: "+oldjson);
            }             
        });              
    }
    updateDash();
    setInterval(updateDash, 5000);
});