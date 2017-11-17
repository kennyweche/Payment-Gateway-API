<?php

//Flaw
//DSTV requires mobile number from destination account
//

//$credentials = array("username"=>"XXXYYYZZZ123@"); //This tells us the source -Roamtech
$credentials = array("username"=>"safaricom_API_user", 'password'=>'safaricom_API_user'); //This tells us the source - Safaricom
//$credentials = array("username"=>"jamii-lotto-user", 'password'=>'jamii-lotto-user'); //This tells us the source - Safaricom
//$credentials = array("username"=>"ewallet_user", 'password'=>'ewallet_user'); //This tells us the source - Safaricom
//$credentials = array("username"=>"mzinga", 'password'=>'mzinga'); //This tells us the source - Safaricom
//$credentials = array("username"=>"airtel_user", 'password'=>'a1rt3lus3r'); //This tells us the source - Safaricom
//$credentials = array("username"=>"betika_api", 'password'=>'betika_api'); //This tells us the source - Safaricom
#$credentials = array("username"=>"roamtech_user", 'password'=>'ro@mt3ch_us3r'); //This tells us the source - Safaricom
#$credentials = array("username"=>"roamtech_user", 'password'=>'roamtech_user'); //This tells us the source - Safaricom
//$credentials = array("username"=>"");
//$credentials = array();
#$credentials = array("username"=>"");
/*$packet = array(
 	"destination"=>"MPESA",//DSTV//SAF_AIRTIME//SAF_B2C
	"destination_account"=>"254711240985",//123456789012//254711240985//254711240985
	"payment_date"=>date('Y-m-d H:i:s'),//..//..//
	"amount"=>7500,//..//100//..
	"channel_id"=>1,//2//3//4
	"reference_number"=>"DXTY0099F",//XDC11234567//1222333//23456199PPA
	"narration"=>"B2C Withdrawal for customer"//DSTV//AIRTIME//SAFWITHDRAWAL
);

$packet = array(
	"source_account"=>"254731240985",
        //"destination"=>"BETIKA_AIRTEL_WD",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination"=>"BETIKA_AIRTEL_DEP",//"SAF_AIRTIME",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254731240985",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>rand(10,100),//..//100//..
        "channel_id"=>4,//3,//2//3//4
        "reference_number"=>"C2B_A".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Betika Deposit"//DSTV//AIRTIME//SAFWITHDRAWAL
);
$packet = array(
        "source_account"=>"254780597919",
        "destination"=>"ROAMTECH_AIRTEL_B2C",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254780597919",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>10,//rand(10,100),//..//100//..
        "channel_id"=>3,//3,//2//3//4
        "reference_number"=>"PG".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Testing Airtel Money withdrawal"//DSTV//AIRTIME//SAFWITHDRAWAL
);
$packet = array(
        "source_account"=>"254711240985",
        "destination"=>'MPESA',//"ROAMTECH_SAF_B2C",//"MPESA",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254711240985",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>10,rand(10,100),//..//100//..
        "channel_id"=>1,//3,//2//3//4
        "reference_number"=>"B2C".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Betika Saf withdrawal",//DSTV//AIRTIME//SAFWITHDRAWAL
	"extra"=>array("shortcode"=>'884838'),
); 

$packet = array(
        "source_account"=>"254711240985",
        #"destination"=>"JAMIILOTTO_SAFARICOM_AIRTIME",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination"=>"SAFARICOM_AIRTIME",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254711240985",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>rand(10,100),//..//100//..
        "channel_id"=>6,
        "reference_number"=>"TOPUP_".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Airtime bonus"//DSTV//AIRTIME//SAFWITHDRAWAL
);

*///---WALLET
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

/*$packet = array(
        "source_account"=>"699699",
        "destination"=>'EWALLET_SAF_WITHDRAWAL',//"ROAMTECH_SAF_B2C",//"MPESA",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254734889991",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>100,//..//100//..
        "channel_id"=>1,//3,//2//3//4
        "reference_number"=>"B2C".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"EWallet Saf withdrawal",//DSTV//AIRTIME//SAFWITHDRAWAL
        "extra"=>array("business_number"=>'699699'),
);

$packet = array(
        "source_account"=>"254711240985",
        "destination"=>'BONYEZA_SAF_AIRTIME',//'BONYEZA_SAF',//"MTICKETS_SAF_DEP",//"BONYEZA",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254711240985",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>rand(10,100),//..//100//..
        "channel_id"=>6,//1,
        "reference_number"=>"BON_".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Content purchase",//DSTV//AIRTIME//SAFWITHDRAWAL
	"extra"=>array("names"=>"Kim Kiogora ", "id"=>"b2ed3ea4f0ff6d58054ca42556b285e1", "business_number"=>"889990")
);

$packet = array(
        "source_account"=>"254711240985",
        "destination"=>'BONYEZA_SAF_MPESA',//'BONYEZA_SAF',//"MTICKETS_SAF_DEP",//"BONYEZA",//DSTV//SAF_AIRTIME//SAF_B2C
        "destination_account"=>"254711240985",//123456789012//254711240985//254711240985
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//
        "amount"=>rand(10,100),//..//100//..
        "channel_id"=>1,
        "reference_number"=>"BON_".date('YmdHis'),//XDC11234567//1222333//23456199PPA
        "narration"=>"Content purchase",//DSTV//AIRTIME//SAFWITHDRAWAL
        "extra"=>array("names"=>"Kim Kiogora ", "id"=>"b2ed3ea4f0ff6d58054ca42556b285e1", "business_number"=>"889990")
);


$packet = array(                                                                                
        "source_account"=>"254711240985",                                                       
        "destination"=>'BONYEZA_AIRTEL_AIRTIME',//'BONYEZA_SAF'                                                                                      
        "destination_account"=>"254711240985",//123456789012//254711240985//254711240985                       
        "payment_date"=>date('Y-m-d H:i:s'),//..//..//                                                               
        "amount"=>rand(10,100),//..//100//..                                                    
        "channel_id"=>6,                                                                        
        "reference_number"=>"BON_".date('YmdHis'),//XDC11234567//1222333//23456199PPA           
        "narration"=>"Content purchase",//DSTV//AIRTIME//SAFWITHDRAWAL
       "extra"=>array("names"=>"Kim Kiogora ", "id"=>"b2ed3ea4f0ff6d58054ca42556b285e1", "business_number"=>"889990")
);
*/

$payload = array("credentials"=>$credentials,"packet"=>$packet);
//$payload = array("credentials"=>NULL,"packet"=>$packet);
//$payload = array("packet"=>$packet);

//$payload = array("credentials"=>$credentials);

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

