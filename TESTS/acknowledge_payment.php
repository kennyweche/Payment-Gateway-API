<?php

$credentials = array("username"=>"betika_api","password"=>"betika_api"); //This tells us the source - Safaricom
//$credentials = array("username"=>"saf_user","password"=>"saf_user"); //This tells us the source - Safaricom
//$credentials = array("username"=>"bonyeza_user_api","password"=>"b0ny3z@_us3r_@p1"); //This tells us the source - Safaricom
//$credentials = array("username"=>"mzinga","password"=>"mzinga"); //This tells us the source - Safaricom
//$credentials = array("username"=>"airtel_user","password"=>"a1rt3lus3r"); //This tells us the source - Safaricom
//$credentials = array("username"=>"safaricom_API_user", 'password'=>'safaricom_API_user'); 
//$credentials = array("username"=>"roamtech_user", 'password'=>'roamtech_user'); 
$packet = array(
        "requestlogID" =>7117,
        "reference_number"=>"EWALLET_20170308120731",//XDC11234567//1222333//23456199PPA
        "status_code" => 123, // either 123, 126 or 124
        "narration"=>"Payment Success"//DSTV//AIRTIME//SAFWITHDRAWAL
);


$payload = array("credentials"=>$credentials,"packet"=>$packet);
$data_string = json_encode($payload);

print_r($data_string);
#die();
$ch = curl_init('http://127.0.0.1:5000/ack_money');                                                                      
//$ch = curl_init('http://sms.roamtech.com:5002/ack_money');                                                                      
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
    'Content-Type: application/json',                                                                                
    'Content-Length: ' . strlen($data_string))                                                                       
);                                                                                                                   

echo "\n\nResult is \n\n";                                                                                                                     
$result = curl_exec($ch);

if ( !empty($result) ) {
    print_r($result);
} else {
    echo "\nNo response. Either you have no connection or API is not responding\n";
}
echo "\n\n";
