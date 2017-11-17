from flask import Flask
import logging, ssl
from flask_restful import Api
from api import SendMoney, ACK, Echo

app = Flask(__name__)
app.config['db_server'] = "localhost"
app.config['db_user'] = "root"
app.config['db_password'] = "portmore254"
app.config['db_name'] = "paymentgtV1"

api = Api(app)
#api.add_resource(Echo, '/create_invoice')
#api.add_resource(Echo, '/fetch_invoice')
api.add_resource(SendMoney, '/send_money')
api.add_resource(ACK, '/ack_money')
api.add_resource(Echo, '/echo')

"""
Auth URL
"""
app.config['auth_url'] = 'http://sms.roamtech.com/accountmanager/public/users/login'
app.config['auth_id'] = 2
app.config['allowed_override_id'] = 3

"""
Setup RabbitMQ for background tasks
"""
app.config['rabbit_mq_server'] = 'localhost'
app.config['rabbit_mq_port'] = 5672

app.config['payments_queue'] = 'payments_queue'
app.config['callback_queue'] = 'callback_queue'
app.config['notification_queue'] = 'notification_queue'

#app.config['rabbit_mq_user'] = 'bobby'
#app.config['rabbit_mq_pass'] = 'toor123'
app.config['rabbit_mq_user'] = 'guest'
app.config['rabbit_mq_pass'] = 'guest'

"""
Setup RabbitMQ for background tasks
"""
app.config['redis_server'] = 'localhost'
app.config['redis_port'] = 6379

"""
Setup logging
"""
app.config['info_logs'] = "/var/log/flask/roamtech/info_gateway.log"
app.config['error_logs'] = "/var/log/flask/roamtech/error_gateway.log"

"""
Setup placeholders
"""
app.config['placeholders'] = {
    '^TRANSACTIONID^': 'SELECT transactionID FROM transactions WHERE requestLogID=%d',
    '^RECEIPTNO^': 'SELECT receipt_number FROM transactions WHERE requestLogID=%d',
    '^NARRATION^': 'SELECT narration FROM request_logs WHERE requestLogID=%d',
    '^SOURCEACCOUNT^': 'SELECT source_account FROM request_logs WHERE requestLogID=%d',
    '^DESTACCOUNT^': 'SELECT destination_account FROM request_logs WHERE requestLogID=%d'
}

"""
Setup the handler
"""
handlerInfo = logging.FileHandler(app.config['info_logs'])
formatter = logging.Formatter('%(asctime)s | %(name)s_%(levelname)s | %(message)s')
handlerInfo.setFormatter(formatter)
app.logger.addHandler(handlerInfo)
app.logger.setLevel(logging.DEBUG)

"""
Entry to application functionality
"""
if __name__ == "__main__":
    s_ip = "127.0.0.1"
    s_port = 5000
    #context = ('certs/gcert.pem', 'certs/gkey.pem')
    #app.run(ssl_context=context, host=s_ip, port=s_port, threaded=True)
    #app.run(ssl_context='adhoc', host=s_ip, port=s_port, threaded=True)
    app.run(host=s_ip, port=s_port, threaded=True)
    