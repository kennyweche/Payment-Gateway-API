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
    _credentials = None

    # constructor
    def __init__(self, credentials, _murl, logger, ch, method, data):
        """Pass your data here"""
        self._credentials = credentials
        self._data = data
        self._ch = ch
        self._method = method
        self._logger = logger
        self._murl = _murl

    '''
    Log a message.
    '''
    def log_message(self, message):
        self._logger.info('%s' % str(message))

    '''
    Process the payment
    '''
    def ack_payment(self, requestLogID, ref_no, final_status, narration):
        self.log_message("Formulating ACK request #####")

        packet = {
            'requestlogID': requestLogID,
            'reference_number': ref_no,
            'status_code': final_status,
            'narration': narration
        }
        payload = {'credentials': self._credentials, 'packet': packet }
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
        mpesa_id = self.get_item(self._data, 'OriginatorConversationID')
        _p_arr = str(mpesa_id).split('-')
        try:
            _requestLogID = int(_p_arr[3])
        except:
            self.log_message("Error extracting request log ID -> PANIC")
            return
        _refNo = self.get_item(self._data, 'TransactionID')
        _mpesa_receipt_no = self.get_item(self._data, 'ConversationID')
        _narration = self.get_item(self._data, 'ResultDesc') + '. Receipt no-' + _mpesa_receipt_no
        _responsecode = self.get_item(self._data, 'ResultCode')

        self.log_message("MPESA ResponseCode %s , Message %s" % (_responsecode, _narration))
        if _responsecode == '0':
            _status = '123'
        elif _responsecode == 'SVC001':
            _status = '126'
        else:
            _status = '124'
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
