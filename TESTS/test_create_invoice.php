<?php

$credentials = array("username"=>"roamtech_user", 'password'=>'roamtech_user'); //This tells us the source - Safaricom

$packet = array(      
	"invoice_number"=>"SVC".date("YmdHis"),                                                                          
        "invoice_account"=>"254711240985",                                                       
        "destination"=>'UAP_INSURANCE',//'BONYEZA_SAF'                                                                                      
        "due_date"=>'2017-02-10',//..//..//
	"message"=>"Dear customer, your bill #SVC0001 of amount KES 2340/= is ready. Dial *135# to pay or use the iHealth mobile app",                                                               	 "amount"=>rand(10,100),
);


$payload = array("credentials"=>$credentials,"packet"=>$packet);

$data_string = json_encode($payload,JSON_PRETTY_PRINT);

print_r($data_string);
echo "\n";
die();
$ch = curl_init('http://127.0.0.1:5000/send_money');                                                                      
//$ch = curl_init('http://sms.roamtech.com:5002/send_money');                                                                      
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

