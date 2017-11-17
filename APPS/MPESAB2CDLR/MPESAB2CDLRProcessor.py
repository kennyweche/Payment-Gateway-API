import pika
import logging
import json
import requests
import sys
import time
import datetime
from threading import Thread

'''
Use thread-pool libraries from http://github/kim.kiogora
'''
from QueuePool import QueueManager
from TaskMan import Task


class MPESAB2CDLRProcessor:
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
    _thread_pool = None

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

        '''
        Initialize the thread pool with 3 threads
        '''
        self._thread_pool = QueueManager(3)

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

    # Creates a simple Runnable that holds a Job object that worked on by the
    # children threads
    def create_task(self, ch, method, data):
        """Pass your data to the worker"""
        credentials = {
            "username": self.username,
            "password": self.password
        }
        task = Task(credentials, self.url, self.logger, ch, method, data)
        task.process()

    '''
    Receive, Push and ACK payment
    '''

    def callback(self, ch, method, properties, body):
        self.log_message("[x] Received request. Processing###")
        self._thread_pool.add_task(self.create_task, ch, method, body)
        q_sz = self._thread_pool.get_queue_size()
        self.log_message("[x] QueueSize on add @ %d request(s)" % q_sz)
        self._thread_pool.wait_completion()
        nq_sz = self._thread_pool.get_queue_size()
        self.log_message("[x] Finished processing. QueueSize on completion @ %d request(s)" % nq_sz)
        time.sleep(float(1))

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

        channel.basic_qos(prefetch_count=10)
        channel.basic_consume(self.callback, queue=self.queue)
        channel.start_consuming()


def main():
    username = 'safaricom_API_user'
    password = 'safaricom_API_user'
    url = "http://localhost:5000/ack_money"
    queue_ = "MPESA_B2C_DLR"
    log_path = "/var/log/flask/roamtech/MPESAB2CProcessor.log"
    server = 'localhost'
    port = 5672
    # rabbit_mq_user = 'bobby'
    # rabbit_mq_pass= 'toor123!'
    rabbit_mq_user = 'guest'
    rabbit_mq_pass = 'guest'
    # init

    pr = MPESAB2CDLRProcessor(username, password, url, queue_, server, port, rabbit_mq_user, rabbit_mq_pass, log_path)
    try:
        pr.run()
    except:
        error = str(sys.exc_info()[1])
        print ("System Shutdown %s" % error)


if __name__ == '__main__':
    try:
        master = Thread(target = main)
        master.start()
    except Exception, errtxt:
        print ' ERROR  ', errtxt
