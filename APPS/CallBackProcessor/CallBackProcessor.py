import pika
import logging
import json
import requests
import sys
import time
import datetime


class CallBackProcessor:
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

    def __init__(self, username, password, url, queue, server, port, rabbit_mq_user, rabbit_mq_pass, log_path):
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

    def send_callback(self, url, post_data):
        self.log_message("Got request, sending #####")
        content = None
        try:
            post_response = requests.post(url=url, data=post_data)
            content = str(post_response.content)
            self.log_message("Sent Callback request response is %s" % content)
        except:
            _error = str(sys.exc_info()[1])
            self.log_message("Error during processing %s" % _error)
            content = None
        return content

    '''
    Receive, Push and ACK payment
    '''

    def callback(self, ch, method, properties, body):
        self.log_message("[x] Received %s" % str(body))
        self.log_message("[x] Extracting payload >>>")
	
        try:
            _json_body = json.loads(body)
            _url = _json_body['url']
            _status = _json_body['status']
            _trx = _json_body['id']
        except:
            _error = str(sys.exc_info()[1])
            self.log_message("Error during processing %s" % _error)
	    ch.basic_ack(delivery_tag=method.delivery_tag)
            return
	
	if _url is None or _url == '' or _url == 'None':
	    self.log_message("[x] Invalid URL close request") 
	    ch.basic_ack(delivery_tag=method.delivery_tag)
	    return

        _body = {
            'status': _status,
            'id': _trx,
	    'request': 'dlr',
        }
	#ch.basic_ack(delivery_tag=method.delivery_tag)
	#return
        response = self.send_callback(_url,json.dumps(_body))
        if response is not None:
            self.log_message("Request completed OK -->%s  #"  % response)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            self.log_message("Response not OK, will retry #")
	    ch.basic_ack(delivery_tag=method.delivery_tag)
            #while True:
            #    response = self.send_callback(body)
            #    if response is not None:
            #        ch.basic_ack(delivery_tag=method.delivery_tag)
            #        break
            #    time.sleep(float(5))

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

        channel.basic_qos(prefetch_count=100)
        channel.basic_consume(self.callback, queue=self.queue)
        channel.start_consuming()


def main():
    username = ''
    password = ''
    url = ''
    queue_ = "callback_queue"
    log_path = "/var/log/flask/roamtech/CallBackProcessor.log"
    server = 'localhost'
    port = 5672
    # rabbit_mq_user = 'bobby'
    # rabbit_mq_pass= 'toor123!'
    rabbit_mq_user = 'guest'
    rabbit_mq_pass = 'guest'
    # init

    pr = CallBackProcessor(username, password, url, queue_, server, port, rabbit_mq_user, rabbit_mq_pass, log_path)
    try:
        pr.run()
    except:
        error = str(sys.exc_info()[1])
        print ("System Shutdown %s" % error)


if __name__ == '__main__':
    main()
