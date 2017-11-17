<?php

$credentials = array("username"=>"safaricom_API_user", 'password'=>'safaricom_API_user'); //This tells us the source - 
$packet = array(
        "source_account"=>"699699",
        "destination"=>"EWALLET_SAF_DEP",//DSTV//SAF_AIRTIME//SAF_B2C
        //"destination_account"=>"254721246987",//123456789012//254711240985//254711240985
        //"destination_account"=>"254723240986",//123456789012//254711240985//254711240985
        "destination_account"=>"254711889991",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>1.00,//..//100//..
        "channel_id"=>2,
        "reference_number"=>"EW_".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"EWallet Deposit",//DSTV//AIRTIME//SAFWITHDRAWAL
	"extra"=>array("account_no"=>"01'91'89","business_number"=>'699699', "names"=>"James Nga\"nga")
);

$payload = array("credentials"=>$credentials,"packet"=>$packet);

$data_string = json_encode($payload,JSON_PRETTY_PRINT);

print_r($data_string);
echo "\n";
//die();
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

