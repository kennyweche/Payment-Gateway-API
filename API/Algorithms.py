from datetime import datetime
import pika
import json
import sys

class PaymentAlgorithms:
    redis_obj = None
    db_obj = None

    """
    Constructor
    """
    def __init__(self, redis_obj, db_obj):
        self.redis_obj = redis_obj
        self.db_obj = db_obj

    '''
    Run an echo test
    1. Check connectivity - DB, queue, Redis
    2. Run DB select
    3. Respond back
    '''
    def run_echo_test(self):
        results = {
            'DB': {
                'connection': {
                    'status': 'pass',
                    'time': '0.001s'
                },
                'query': {
                    'status': 'pass',
                    'time': '0.001s'
                }

            },
            'MQ': {
                'connection': {
                    'status': 'pass',
                    'time': '0.001s'
                },
                'insert': {
                    'status': 'pass',
                    'time': '0.001s'
                }

            },
            'Redis': {
                'connection': {
                    'status': 'pass',
                    'time': '0.001s'
                },
                'insert': {
                    'status': 'pass',
                    'time': '0.001s'
                }

            },
        }
        return results

    '''
    Schedule profile.
    '''
    def schedule_profiling(self, source, **kwargs):
        pass

    '''
    Save to Redis
    '''
    def cache_data(self, key, data):
        try:
            self.redis_obj.push(key, json.dumps(data))
        except:
            pass

    '''
    Get data from Redis
    '''
    def retrieve_cached_data(self, key):
        try:
            return json.loads(self.redis_obj.pop(key))
        except:
            return None

    '''
    Clean message
    '''
    @staticmethod
    def clean_message(self, app, message, requestlogid):
        message = str(message)
        placeholders = app.config['placeholders']
        if placeholders is None:
            self.write_log(app, "No placeholder(s) found", "info")
            return message
        self.write_log(app, "placeholders ==> %s  ####" % str(placeholders), "info")

        self.write_log(app, "checking message %s for placeholders ####" % message, "info")

        for d, v in enumerate(placeholders):
            t_sql = placeholders[v] % requestlogid
            self.write_log(app, "formatted sql=> %s for placeholder %s ####" % (v, t_sql), "info")
            '''
            fetch item from database
            '''
            self.write_log(app, "find placeholder replacement from database", "info")
            db_item = self.db_obj.do_select(t_sql)
            self.write_log(app, "response from database => %s" % str(db_item), "info")
            if db_item['data'] is not None:
                item = str(db_item['data'][0])
                self.write_log(app, "replace placeholder %s with db item %s" % (v, item), "info")
                message = message.replace(v, item)
            self.write_log(app, "final message back to customer is %s" % message, "info")
        return message

    """
    Log an error
    """
    @staticmethod
    def write_log(app, msg, msg_type):
        t = datetime.now()
        str_time = t.strftime("%Y-%m-%d %H:%M:%S")
        msg = str_time + " | " + msg
        if msg_type == 'error':
            app.logger.error(msg)
        else:
            app.logger.info(msg)

    """
    Retrieve status description from db or redis
    """
    def get_status_description(self, app, status_code):
        item = ''
        try:
            redis_data = self.redis_obj.pop(status_code)
            if redis_data is not None:
                return redis_data
            else:
                sql = "SELECT description from statusCodes WHERE code='%s'" % status_code
                desc = self.db_obj.do_select(sql)

                if desc is not None:
                    item = desc['data'][0]
                    """
                    Save to cache, will be refreshed in an Hour
                    """
                    self.redis_obj.push(status_code, item)
                """
                Return db description
                """
                return item
        except:
            error = str(sys.exc_info()[1])
            self.write_log(app, "Error -> %s " % str(error), "error")
            return item

    '''
    Check parameters
    '''
    @staticmethod
    def check_param(payload, param):
        try:
            item = payload[param]
            return True
        except:
            return False

    '''
    Push to RabbitMQ.
    Redone: Optimize so you don't have to declare a queue every time
    '''
    def push_to_queue(self, app, my_queue, data):
        self.write_log(app, "Sending data %s to rabbit mq ..." % str(data), "info")
        try:
            self.write_log(app, "Check MQ connection >>>>>", "info")
            r_credentials = pika.PlainCredentials(app.config['rabbit_mq_user'], app.config['rabbit_mq_pass'])
            parameters = pika.ConnectionParameters(app.config['rabbit_mq_server'], app.config['rabbit_mq_port'], '/',
                                                   r_credentials)

            connection = pika.BlockingConnection(parameters)
            
            channel = connection.channel()
            redis_data = self.redis_obj.pop(my_queue)
            picked_queue = my_queue
            if redis_data is None:
                channel.queue_declare(queue=my_queue, durable=True)
                self.redis_obj.push(my_queue, my_queue)
            else:
                picked_queue = redis_data

            channel.basic_publish(exchange='', routing_key=picked_queue, body=json.dumps(data),
                                  properties=pika.BasicProperties(delivery_mode=2,))
            channel.close()
            connection.close()
            self.write_log(app, "Data pushed to queue %s OK" % my_queue, "info")
            return 'OK'
        except:
            error = str(sys.exc_info()[1])
            self.write_log(app, "Error -> %s " % str(error), "error")
            return 'FAIL'
