<?php
$ch = curl_init('http://127.0.0.1:5000/echo');                                                                      
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "GET");                                                                     
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      

echo "\n\nResult is \n\n";                                                                                                                     
$result = curl_exec($ch);

if ( !empty($result) ) {
    print_r($result);
} else {
    echo "\nNo response. Either you have no connection or API is not responding\n";
}
echo "\n\n";
