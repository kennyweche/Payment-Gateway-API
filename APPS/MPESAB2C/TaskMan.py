import requests
import sys
import json

class Task:
    # variables
    _data = None
    _ch = None
    _method = None
    _logger = None
    _murl = None

    # constructor
    def __init__(self, _murl, logger, ch, method, data):
        """Pass your data here"""
        self._data = data
        self._ch = ch
        self._method = method
        self._logger = logger
        self._murl = _murl

    def log_message(self, message):
        self._logger.info('%s' % str(message))

    '''
    Process the payment
    '''

    def send_request(self, url, post_data):
        self.log_message("Got request, sending #####")
        content = None
        try:
            post_response = requests.post(url=url, data=post_data)
            content = str(post_response.content)
            self.log_message("Sent request response is %s" % content)
        except:
            _error = str(sys.exc_info()[1])
            self.log_message("Error during processing %s" % _error)
            content = None
        return content

    '''
    Process the payment
    '''
    def ack_payment(self, requestLogID, ref_no, final_status, narration):
        self.log_message("Formulating ACK request #####")
        credentials = {
            'username': 'safaricom_API_user',
            'password': 'safaricom_API_user'
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
            post_response = requests.post(url=self._murl, data=post_data)
            self.log_message("Sent ACK request response is %s" % str(post_response.content))
        except:
            _error = str(sys.exc_info()[1])
            self.log_message("Error during processing %s" % _error)

    def process(self):
        """Do something with your data, mydata variable """
        self.log_message("Thread received %s" % str(self._data))
        _url = self.get_item(self._data, 'endpoint')
        _requestLogID = self.get_item(self._data, 'requestLogID')
        _refNo = self.get_item(self._data, 'reference')
        _msisdn = self.get_item(self._data, 'destination_account')
        _amount = self.get_item(self._data, 'amount')
        _extra = self.get_item(self._data, 'extra')
        _shortcode = self.get_inner_item(_extra, 'shortcode')

        _b2c_params = {
            "reference": _refNo,
            "MSISDN": _msisdn,
            "amount": _amount,
            "shortcode": _shortcode
        }
        _json_payload = json.dumps(_b2c_params)

        self.log_message("B2C params is %s" % str(_json_payload))

        _response = self.send_request(_url, _json_payload)
        self.log_message("Response from API is %s" % str(_response))
        if _response is None:
            self.log_message("Response from API is %s" % str(_response))
            self.ack_payment(_requestLogID, _refNo, '126', 'Manual Reconciliation Required. Response was empty')
            self._ch.basic_ack(delivery_tag=self._method.delivery_tag)
            return

        _details = self.get_item(_response, 'Details')
        _responsecode = self.get_inner_item(_details, 'ResponseCode')
        _narration = self.get_inner_item(_details, 'ResponseDesc')

        if _details is None:
            self.log_message("Details parameter was empty.")
            self.ack_payment(_requestLogID, _refNo, '126', 'Manual Reconciliation Required. Response was empty')
            self._ch.basic_ack(delivery_tag=self._method.delivery_tag)
            return

        self.log_message("MPESA ResponseCode %s , Message %s" % (_responsecode, _narration))

        if _responsecode == '0':
            _status = '148'
        else:
            _status = '124'
            _narration = 'Failed'

        self.ack_payment(_requestLogID, _refNo, _status, _narration)

        self._ch.basic_ack(delivery_tag=self._method.delivery_tag)

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
