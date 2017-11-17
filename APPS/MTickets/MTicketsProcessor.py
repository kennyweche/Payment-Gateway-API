import pika
import logging
import json
import requests
import sys
import time
import datetime

class MTicketsProcessor:
    username = ''
    password = ''
    url = ''
    queue = ''
    log_path = ''
    logger = None
    rabbit_mq_user = None
    rabbit_mq_pass = None
    server = 'localhost'
    port = 5672

    def __init__(self, username, password, url, queue,server, port, rabbit_mq_user, rabbit_mq_pass, log_path):
        self.username = username
        self.password = password
        self.url = url
        self.server = server
        self.port = port
        self.rabbit_mq_user = rabbit_mq_user
        self.rabbit_mq_pass = rabbit_mq_pass
        self.queue = queue
        self.log_path = log_path

        self.logger = logging.getLogger(self.__class__.__name__)
        handlerInfo = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(asctime)s | %(name)s_%(levelname)s | %(message)s')
        handlerInfo.setFormatter(formatter)
        self.logger.addHandler(handlerInfo)
        self.logger.setLevel(logging.DEBUG)
        self.log_message("Processor starting up ######")

    '''
    Log a message
    '''
    def log_message(self, message):
        self.logger.info('%s' % str(message))

    '''
    Process the payment
    '''
    def ack_payment(self, requestLogID, ref_no, final_status, narration):
        self.log_message("Formulating ACK request #####")
        credentials = {
            'username': self.username,
            'password': self.password
        }
        packet = {
            'requestlogID': requestLogID,
            'reference_number': ref_no,
            'status_code': final_status,
            'narration': narration
        }
        payload = {'credentials': credentials, 'packet': packet }
        post_data = json.dumps(payload)
        self.log_message("Formulated ACK request, sending #####")
        try:
            post_response = requests.post(url=self.url, data=post_data)
            self.log_message("Sent ACK request response is %s" % str(post_response.content))
        except:
            _error = str(sys.exc_info()[1])
            self.log_message("Error during processing %s" % _error)

    '''
    Get item from JSON packet
    '''
    def get_item(self, dataset, key):
        try:
            json_body = json.loads(dataset)
            value = json_body[key]
        except:
            value = None
        return value

    '''
    Get item from JSON packet
    '''
    def get_inner_item(self, dataset, key):
        try:
            value = dataset[key]
        except:
            value = None
        return value

    '''
    Receive, Push and ACK payment
    '''
    def callback(self, ch, method, properties, body):
        self.log_message("[x] Received %s" % str(body))
        self.log_message("[x] Extracting payload >>>")

        _url = self.get_item(body, 'endpoint')
        _requestLogID = self.get_item(body, 'requestLogID')
        _refNo = self.get_item(body, 'reference')
        _msisdn = self.get_item(body, 'msisdn')
        _amount = self.get_item(body, 'amount')
        _billref = self.get_item(body, 'destination_account')
        _extra = self.get_item(body, 'extra')

        self.log_message("[x] Extra %s >>>" % _extra)

        _id = self.get_inner_item(_extra, 'id')
        _names = self.get_inner_item(_extra, 'names')

        self.log_message("[x] Sending payload >>>")
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        de_payload = {
            'msisdn': _msisdn,
            'names': _names,
            'mpesa_txid': _id,
            'mpesa_ref': _billref,
            'mpesa_amount': _amount,
            'timestamp': st,
        }
        self.log_message("[x] Payload -> %s >>>" % str(de_payload))
        try:
            #response = requests.post(url=_url, data=de_payload)
            #if response.status_code == 201:
            response = 401
            if response == 200:
                status = 123
                _narration = 'Payment Successful'
            else:
                status = 124
                _narration = 'Payment Failed'
        except:
            _error = str(sys.exc_info()[1])
            status = 126
            _narration = 'An unknown error occurred'
            self.log_message("Except->There appears to be an issue with the payload => %s" % _error)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        if _requestLogID is not None and _refNo is not None:
            self.ack_payment(_requestLogID, _refNo, status, _narration)
        else:
            self.log_message("There appears to be an issue with the payload")

        ch.basic_ack(delivery_tag=method.delivery_tag)

        self.log_message("Request completed OK #")

    '''
    Run the application
    '''
    def run(self):
        self.log_message("Processor started up OK ..starting consumer thread ###")

        r_credentials = pika.PlainCredentials(self.rabbit_mq_user, self.rabbit_mq_pass)
        parameters = pika.ConnectionParameters(self.server, self.port, '/', r_credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)

        self.log_message('[*] Waiting for requests')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.callback, queue=self.queue)
        channel.start_consuming()

username = 'mtickets_api_user'
password = 'mt1ck3ts_ap1_us3r'
url = "http://localhost:5000/ack_money"
queue_ = "MTICKETS"
log_path = "/var/log/flask/roamtech/MTicketsProcessor.log"
server = 'localhost'
port = 5672
#rabbit_mq_user = 'bobby'
#rabbit_mq_pass= 'toor123!'
rabbit_mq_user = 'guest'
rabbit_mq_pass = 'guest'
#init

pr = MTicketsProcessor(username, password, url, queue_, server, port, rabbit_mq_user, rabbit_mq_pass, log_path)
try:
    pr.run()
except:
    error = str(sys.exc_info()[1])
    print ("System Shutdown %s" % error)

