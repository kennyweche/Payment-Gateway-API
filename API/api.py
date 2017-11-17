from flask import request
from flask_restful import Resource
from StatusCodes import StatusCodes
from Redis import RCache
from Algorithms import PaymentAlgorithms
from DBConnector import Connector
from flask import current_app as app
import json
import sys
from Authentication import Auth
from datetime import datetime
import time

'''
All applications call this class via function send_money t be able to route payments via the Roamtech Payment
Gateway
'''


class SendMoney(Resource):
    def __init__(self):
        self.amount_val = 0
        self.chan_id = None
        # setup redis
        self.redis = RCache(app.config['redis_server'], app.config['redis_port'])
        # Setup database
        self.connector = Connector(app.config['db_server'], app.config['db_user'], app.config['db_password'],
                                   app.config['db_name'])
        # setup algorithms
        self.alg = PaymentAlgorithms(self.redis, self.connector)
        super(SendMoney, self).__init__()

    def post(self):
        #global amount_val
        #global client_id
        start_time = time.time()
        self.alg.write_log(app, "Request received ,extracting...", "info")
        data = dict()
        try:
            str_request = str(request.data)
            json_req = json.loads(str_request)
            if not self.alg.check_param(json_req, 'credentials'):
                data['statusCode'] = StatusCodes.MISSING_CREDENTIAL_PARAMS
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_CREDENTIAL_PARAMS)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            credentials = json_req['credentials']
            if credentials is None:
                data['statusCode'] = StatusCodes.MISSING_CREDENTIAL_PARAMS
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_CREDENTIAL_PARAMS)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Extracting username ", "info")
            if not self.alg.check_param(credentials, 'username'):
                self.alg.write_log(app, "username not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_USERNAME_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_USERNAME_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            username = str(credentials['username'])
            self.alg.write_log(app, "Extracted username %s" % username, "info")
            self.alg.write_log(app, "Validate extracted username %s" % username, "info")
            if username is None or username == '':
                self.alg.write_log(app, "username not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_USERNAME_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_USERNAME_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if not self.alg.check_param(credentials, 'password'):
                self.alg.write_log(app, "Password not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_PASSWORD_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PASSWORD_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            password = str(credentials['password'])
            self.alg.write_log(app, "Extracted password ********", "info")
            self.alg.write_log(app, "Validate extracted password######", "info")
            if password is None or password == '':
                self.alg.write_log(app, "password not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_PASSWORD_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PASSWORD_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Authenticating user %s ..." % username, "info")
            '''
            Confirm user in DB first
            '''
            confirm_user_sql = "SELECT userID, userType FROM users WHERE username='%s' AND password='%s'" \
                               % (username, password)
            cache_item = 'CRED%s%s' % (username, password)
            self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
            confirm_data = self.alg.retrieve_cached_data(cache_item)
            self.alg.write_log(app, "Redis SAYS -> %s" % confirm_data, "info")
            if confirm_data is None:
                self.alg.write_log(app, "GO TO DB -->", "info")
                confirm_res = self.connector.do_select(confirm_user_sql)
                confirm_data = confirm_res['data']
                if confirm_data is not None:
                    self.alg.cache_data(cache_item, confirm_data)

            self.alg.write_log(app, "Auth data -> %s" % str(confirm_data), "info")
            if confirm_data is None:
                self.alg.write_log(app, "Set of credentials not found. Authentication failure", "info")
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if str(confirm_data[1]) != 'API':
                self.alg.write_log(app, "User not allowed to access API", "info")
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            """
            AUTH
            """
            auth = Auth(app, self.alg, username, password)
            auth_status = auth.is_authenticated()
            if auth_status is False:
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            csql = "SELECT c.clientID, c.clientName, u.status, c.status from users u inner join clients c on " \
                   "u.clientID=c.clientID where u.username='%s' AND u.userType='API'" % username

            cache_item = 'PROP%s%s' % (username, password)
            self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
            cdata = self.alg.retrieve_cached_data(cache_item)
            self.alg.write_log(app, "Redis SAYS -> %s" % cdata, "info")
            if cdata is None:
                cdata = self.connector.do_select(csql)
                self.alg.cache_data(cache_item, cdata)

            self.alg.write_log(app, "check auth => %s, sql => %s" % (str(cdata), csql), "info")
            status = cdata['status']
            if status == 'FAIL' or cdata['data'] is None:
                self.alg.write_log(app, "Authentication failed..Check client configurations", "info")
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            auth_data = cdata['data']
            client_id = auth_data[0]
            source = auth_data[1]
            user_status = auth_data[2]
            client_status = auth_data[2]

            if client_status == StatusCodes.INACTIVE:
                self.alg.write_log(app, "The client is not active", "info")
                data['statusCode'] = StatusCodes.INACTIVE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if user_status == StatusCodes.INACTIVE:
                self.alg.write_log(app, "The user is not active", "info")
                data['statusCode'] = StatusCodes.INACTIVE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Username %s is authenticated, source => %s, checking payload provided ..."
                               % (username, source), "info")

            if not self.alg.check_param(json_req, 'packet'):
                self.alg.write_log(app, "Packet payload not specified ...", "info")
                data['statusCode'] = StatusCodes.MISSING_PACKET_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PACKET_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            packet = json_req['packet']
            if packet is None:
                self.alg.write_log(app, "Packet payload not specified ...", "info")
                data['statusCode'] = StatusCodes.MISSING_PACKET_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PACKET_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "validating packet %s ..." % packet, "info")

            if not self.alg.check_param(packet, 'source_account'):
                data['statusCode'] = StatusCodes.MISSING_SOURCE_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_SOURCE_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                source_account = packet['source_account']
                if source_account == '':
                    data['statusCode'] = StatusCodes.MISSING_SOURCE_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_SOURCE_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            if not self.alg.check_param(packet, 'narration'):
                data['statusCode'] = StatusCodes.MISSING_NARRATION_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_NARRATION_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                narration = packet['narration']
                if narration == '':
                    data['statusCode'] = StatusCodes.MISSING_NARRATION_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_NARRATION_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            if not self.alg.check_param(packet, 'reference_number'):
                data['statusCode'] = StatusCodes.MISSING_REF_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_REF_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            reference_no = packet['reference_number']
            if reference_no is None:
                data['statusCode'] = StatusCodes.MISSING_REF_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_REF_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                if reference_no == '':
                    data['statusCode'] = StatusCodes.MISSING_REF_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_REF_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            if not self.alg.check_param(packet, 'channel_id'):
                data['statusCode'] = StatusCodes.MISSING_CHANNEL_ID_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_CHANNEL_ID_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            channel_id = packet['channel_id']
            global chan_id
            chan_id = 0
            if channel_id is None:
                data['statusCode'] = StatusCodes.MISSING_CHANNEL_ID_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_CHANNEL_ID_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                try:
                    chan_id = int(channel_id)
                    if chan_id <= 0:
                        data['statusCode'] = StatusCodes.INVALID_AMOUNT
                        data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_AMOUNT)
                        resp = data
                        self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                        return resp
                except:
                    error = str(sys.exc_info()[1])
                    self.alg.write_log(app, "Error with the channel id provided %s seems invalid" % str(error),
                                       "error")

            # check that the channel_id exists and is active
            cache_item = 'CHAN%d' % chan_id
            self.alg.write_log(app, "GET FROM Redis -->", "info")
            channel_data = self.alg.retrieve_cached_data(cache_item)
            self.alg.write_log(app, "Redis SAYS -> %s" % channel_data, "info")
            if channel_data is None:
                channel_data = self.connector.do_select('SELECT channelID, status from channel where channelID=%s'
                                                        % chan_id)
                self.alg.cache_data('CHAN%d' % chan_id, channel_data)

            self.alg.write_log(app, "channel data => %s" % str(channel_data), "info")
            if channel_data['status'] == 'FAIL':
                data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if channel_data['data'] is None:
                data['statusCode'] = StatusCodes.INVALID_CHANNEL_ID
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_CHANNEL_ID)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            active = channel_data['data'][1]
            if active == StatusCodes.INACTIVE:
                data['statusCode'] = StatusCodes.INACTIVE_CHANNEL
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE_CHANNEL)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if not self.alg.check_param(packet, 'destination'):
                data['statusCode'] = StatusCodes.MISSING_DESTINATION_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_DESTINATION_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            destination = packet['destination']
            if destination is None:
                data['statusCode'] = StatusCodes.MISSING_DESTINATION_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_DESTINATION_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                if destination == '':
                    data['statusCode'] = StatusCodes.MISSING_DESTINATION_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_DESTINATION_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            if not self.alg.check_param(packet, 'destination_account'):
                data['statusCode'] = StatusCodes.MISSING_DEST_ACC_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_DEST_ACC_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            destination_acc = packet['destination_account']
            if destination_acc is None:
                data['statusCode'] = StatusCodes.MISSING_DEST_ACC_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_DEST_ACC_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                if destination_acc == '':
                    data['statusCode'] = StatusCodes.MISSING_DEST_ACC_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_DEST_ACC_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            if not self.alg.check_param(packet, 'payment_date'):
                data['statusCode'] = StatusCodes.MISSING_PAYMENT_DATE_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PAYMENT_DATE_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            payment_date = packet['payment_date']
            if payment_date is None:
                data['statusCode'] = StatusCodes.MISSING_PAYMENT_DATE_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_PAYMENT_DATE_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                if payment_date == '':
                    data['statusCode'] = StatusCodes.MISSING_PAYMENT_DATE_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_PAYMENT_DATE_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            # check if payment date is past
            self.alg.write_log(app, "Converting payment date %s" % payment_date, "info")
            try:
                formatted_time = datetime.strptime(payment_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            except:
                error = str(sys.exc_info()[1])
                self.alg.write_log(app, "error converting payment date %s. Error => %s" % (payment_date, error),
                                   "error")
                data['statusCode'] = StatusCodes.INVALID_DATE_FORMAT
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_DATE_FORMAT)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            today_is = time.strftime("%Y-%m-%d")

            if formatted_time < today_is:
                data['statusCode'] = StatusCodes.INVALID_PAYMENT_DATE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_PAYMENT_DATE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            amount_val = 0
            if not self.alg.check_param(packet, 'amount'):
                data['statusCode'] = StatusCodes.MISSING_AMOUNT_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_AMOUNT_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            amount = packet['amount']
            if amount is None:
                data['statusCode'] = StatusCodes.MISSING_AMOUNT_PARAM
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_AMOUNT_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                if amount == '':
                    data['statusCode'] = StatusCodes.MISSING_AMOUNT_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.MISSING_AMOUNT_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp
                else:
                    try:
                        amount_val = float(amount)
                        if amount_val <= 0:
                            data['statusCode'] = StatusCodes.INVALID_AMOUNT
                            data['statusDescription'] = self.alg.get_status_description(app,
                                                                                        StatusCodes.INVALID_AMOUNT)
                            resp = data
                            self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                            return resp
                    except:
                        error = str(sys.exc_info()[1])
                        self.alg.write_log(app, "Error with the amount provided %s seems invalid" % str(error),
                                           "error")
                        data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                        data['statusDescription'] = self.alg.get_status_description(app,
                                                                                    StatusCodes.GENERAL_SYSTEM_ERROR)
                        resp = data
                        self.alg.write_log(app, "Response back %s" % resp, "info")
                        return resp
            self.alg.write_log(app, "Amount val is %d" % amount_val, "info")
            '''
            Extra parameters, such as names
            '''
            extras = None
            if self.alg.check_param(packet, 'extra'):
                extras = packet['extra']
                if extras is not None:
                    self.alg.write_log(app, "GOT EXTRAS !", "info")
                    try:
                        extrap = json.dumps(extras)
                        obj = json.loads(extrap)
                        new_extras = {}
                        for i, v in enumerate(obj):
                            ir = str(obj[v]).replace("'", "")
                            ir = ir.replace("\"", "")
                            new_extras[v] = ir
                        extras = json.dumps(new_extras)
                    except:
                        self.alg.write_log(app, "Error converting EXTRAS !", "info")
                        extras = json.dumps(extras)

            """
            heck to see if the transaction exists(duplicates)
            """
            check_sql = "SELECT requestLogID FROM request_logs WHERE external_ref_id='%s'" % reference_no
            self.alg.write_log(app, "Check for duplicate query => %s" % check_sql, "info")
            result = self.connector.do_select(check_sql, False)
            res = result['data']

            self.alg.write_log(app, "Check for duplicate results %s " % str(res), "info")
            if res is not None:
                self.alg.write_log(app, "Duplicate Transaction with ref no %s found " % reference_no, "info")
                data['statusCode'] = StatusCodes.DUPLICATE_TRANSACTION
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.DUPLICATE_TRANSACTION)
                resp = data
                self.alg.write_log(app, "Response back %s" % resp, "info")
                return resp
            else:
                """
                Everything is OK, proceed to insert into the requestLogs and queue
                """
                '''
                confirm the channelID is right
                '''
                self.alg.write_log(app, "Checking provided channelID ####", "info")
                channel_confirm_sql = "select channelID from client_channels where client_channelID = " \
                                      "(select client_channelID from client_channels_reference where code = " \
                                      "'%s')" % destination
                self.alg.write_log(app, "SQL -> %s" % channel_confirm_sql, "info")
                cache_item = 'MAP%s' % destination
                self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
                chan_res = self.alg.retrieve_cached_data(cache_item)
                self.alg.write_log(app, "Redis SAYS -> %s" % chan_res, "info")
                if chan_res is None:
                    result = self.connector.do_select(channel_confirm_sql, False)
                    self.alg.write_log(app, "channelID data =>%s ...." % str(result), "info")
                    chan_res = result['data']
                    self.alg.cache_data(cache_item, chan_res)

                if chan_res is None:
                    self.alg.write_log(app, "Channel not found for specified route. Check configurations for client",
                                       "info")
                    data['statusCode'] = StatusCodes.PAYMENT_ROUTE_NOT_FOUND
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.PAYMENT_ROUTE_NOT_FOUND)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                if int(chan_res[0]) != int(chan_id):
                    self.alg.write_log(app, "Invalid channelID specified. Check configurations for client", "info")
                    data['statusCode'] = StatusCodes.PAYMENT_ROUTE_NOT_FOUND
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.PAYMENT_ROUTE_NOT_FOUND)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                self.alg.write_log(app, "Confirming payment route ....", "info")
                # Is the route enabled ?
                route_check_sql = "select end_point, callback, status, channel_ref_id,queue_name from client_channels_reference" \
                                  " where clientID=%d" \
                                  " and client_channelID = (select client_channelID from client_channels_reference where" \
                                  " code = '%s')" % (client_id, destination)
                self.alg.write_log(app, "SQL -> %s" % route_check_sql, "info")
                cache_item = 'ROUTE%s%d' % (destination, client_id)
                self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
                res = self.alg.retrieve_cached_data(cache_item)
                self.alg.write_log(app, "Redis SAYS -> %s" % res, "info")
                if res is None:
                    result = self.connector.do_select(route_check_sql, False)
                    res = result['data']
                    self.alg.cache_data(cache_item, res)

                self.alg.write_log(app, "payment route data =>%s ...." % str(result), "info")
                if res is None:
                    self.alg.write_log(app, "Payment Route not found. Check configurations for client", "info")
                    data['statusCode'] = StatusCodes.PAYMENT_ROUTE_NOT_FOUND
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.PAYMENT_ROUTE_NOT_FOUND)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                if res[2] != StatusCodes.ACTIVE:
                    self.alg.write_log(app, "Payment Route found is not active. Check configurations for client",
                                       "info")
                    data['statusCode'] = StatusCodes.INACTIVE
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                self.alg.write_log(app, "fetching the queue name #####", "info")
                '''
                Get the queue name
                '''
                queue_name_is = res[4]

                if queue_name_is is None or queue_name_is == '':
                    self.alg.write_log(app, "Error finding queue. Check configurations for client", "info")
                    data['statusCode'] = StatusCodes.NO_QUEUE_NAME_FOUND
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.NO_QUEUE_NAME_FOUND)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                queue_check_sql = "select cc.client_channel_name,cr.rules_endpoint from " \
                                  "client_channels cc left join channel_rules cr on " \
                                  "cc.client_channelID=cr.client_channelID where cc.clientID=%d and " \
                                  "cc.channelID=%d" % (client_id, chan_id)
                self.alg.write_log(app, "query => %s" % queue_check_sql, "info")
                cache_item = 'RULE%d_%d' % (client_id, chan_id)
                self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
                q_data = self.alg.retrieve_cached_data(cache_item)
                self.alg.write_log(app, "Redis SAYS -> %s" % q_data, "info")
                if q_data is None:
                    q_data = self.connector.do_select(queue_check_sql)
                    self.alg.cache_data(cache_item, q_data)

                self.alg.write_log(app, "find validation results =>%s ...." % str(q_data), "info")
                qres = q_data['data']
                if qres is not None:
                    validation_endpoint = qres[1]
                else:
                    validation_endpoint = None

                self.alg.write_log(app, "route confirmed, pushing to request_logs for processing ...", "info")
                ins_sql = "INSERT INTO request_logs (channelID, external_ref_id, amount,source,source_account," \
                          "destination,overalStatus,narration,payment_date,destination_account,extras, date_created, " \
                          "date_modified) values (%d,'%s',%d,'%s','%s','%s','%s','%s','%s','%s','%s',now(),now())" \
                          % (chan_id, reference_no, amount_val, source, source_account, destination,
                             StatusCodes.PAYMENT_QUEUED, narration,
                             payment_date, destination_acc, extras)

                self.alg.write_log(app, "Insert query is => %s" % ins_sql, "info")
                result = self.connector.do_insert(ins_sql)
                self.alg.write_log(app, "Ran insert query, result is %s" % str(result), "info")
                if result is None:
                    self.alg.write_log(app, "No result received after running query", "error")
                    data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp

                self.alg.write_log(app, "Success after running insert query. Checking final status ...", "info")
                # Get status and id
                status = result['status']
                if status == 'FAIL':
                    self.alg.write_log(app, "query failed to execute...PANIC", "info")
                    data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                    resp = data
                    self.alg.write_log(app, "Response back %s" % resp, "info")
                    return resp
                else:
                    self.alg.write_log(app, "query was executed successfully, extract insert id and push to MQ", "info")
                    insert_id = result['data']
                    self.alg.write_log(app, "insert id for ref no %s is %s" % (reference_no, str(insert_id)), "info")

                    transactions_sql = "INSERT INTO transactions (requestlogID,channel_ref_id," \
                                       "date_created,date_modified) values (%d,%d,now(),now())" % (insert_id, res[3])

                    self.alg.write_log(app, "Pushing to transactions table, query => %s" % transactions_sql, "info")
                    tresult = self.connector.do_insert(transactions_sql)
                    self.alg.write_log(app, "Ran insert query, result is %s" % str(tresult), "info")
                    if tresult is None:
                        self.alg.write_log(app,
                                           "Pushing to transactions table failed > PANIC, query %s "
                                           % transactions_sql,
                                           "error")
                        data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                        data['statusDescription'] = self.alg.get_status_description(app,
                                                                                    StatusCodes.GENERAL_SYSTEM_ERROR)
                        resp = data
                        self.alg.write_log(app, "Response back %s" % resp, "info")
                        return resp

                    if result['status'] == 'FAIL':
                        self.alg.write_log(app,
                                           "Pushing to transactions table failed > PANIC, query %s "
                                           % transactions_sql,
                                           "error")
                        data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                        data['statusDescription'] = self.alg.get_status_description(app,
                                                                                    StatusCodes.GENERAL_SYSTEM_ERROR)
                        resp = data
                        self.alg.write_log(app, "Response back %s" % resp, "info")
                        return resp

                    tinsert_id = result['data']
                    try:
                        extras = json.loads(extras)
                    except:
                        self.alg.write_log(app, "FAILED TO CONVERT EXTRAS", "info")
                        pass
                    mq_data = {
                        'requestLogID': insert_id,
                        'transactionID': tinsert_id,
                        'amount': amount_val,
                        'source': source,
                        'msisdn': source_account,
                        'destination': destination,
                        'destination_account': destination_acc,
                        'payment_date': payment_date,
                        'reference': reference_no,
                        'endpoint': res[0],
                        'callback': res[1],
                        'extra': extras,
                        'queue_name': str(queue_name_is),
                        'validation_endpoint': validation_endpoint
                    }
                    self.alg.write_log(app, "Data to push to queue is %s, pushing" % str(mq_data), "info")
                    ps = self.alg.push_to_queue(app, app.config['payments_queue'], mq_data)
                    self.alg.write_log(app, "Response after pushing to MQ is %s" % ps, "info")
                    if ps == 'FAIL':
                        '''
                        store in db ( re-queue table ) for reprocessing ???
                        '''
                        self.alg.write_log(app, "Push to queue failed, push back to db ####", "info")
                    ##########################################
                    # Update redis

                    ##########################################
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    f_str_el_time = '{:.2f}'.format(elapsed_time)
                    str_el_time = "%s second(s)" % str(f_str_el_time)

                    data['statusCode'] = StatusCodes.PAYMENT_QUEUED
                    data['requestLogID'] = insert_id
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.PAYMENT_QUEUED)
                    resp = data
                    self.alg.write_log(app, "Response back %s. TimeTaken: %s" % (resp, str_el_time), "info")
                    return data
        except:
            self.alg.write_log(app, "Initiating roll back because of error", "error")
            self.alg.write_log(app, "Rolling back ran #####", "error")
            error = str(sys.exc_info()[1])
            self.alg.write_log(app, "Error -> %s " % str(error), "error")
            data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
            data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
            resp = data
            self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
            return resp


'''
A class to acknowledge the sent payments.
Note: API receives payment. Payment is pushed to external processors. Once a status is received from the external
URL, external processors will interpret that status as a success, fail or requiring manual reconciliation by calling
the ACK class through function ack_money
'''


class ACK(Resource):
    def __init__(self):
        # setup redis
        self.redis = RCache(app.config['redis_server'], app.config['redis_port'])
        # Setup database
        self.connector = Connector(app.config['db_server'], app.config['db_user'], app.config['db_password'],
                                   app.config['db_name'])
        # setup algorithms
        self.alg = PaymentAlgorithms(self.redis, self.connector)
        super(ACK, self).__init__()

    def post(self):
        self.alg.write_log(app, "Request received ,extracting...", "info")
        data = dict()
        try:
            str_request = str(request.data)
            json_req = json.loads(str_request)
            self.alg.write_log(app, "Success...", "info")

            if not self.alg.check_param(json_req, 'credentials'):
                data['statusCode'] = StatusCodes.MISSING_CREDENTIAL_PARAMS
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_CREDENTIAL_PARAMS)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            credentials = json_req['credentials']
            if credentials is None:
                data['statusCode'] = StatusCodes.MISSING_CREDENTIAL_PARAMS
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_CREDENTIAL_PARAMS)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Extracting username ", "info")
            if not self.alg.check_param(credentials, 'username'):
                self.alg.write_log(app, "username not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_USERNAME_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_USERNAME_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            username = str(credentials['username'])
            self.alg.write_log(app, "Extracted username %s" % username, "info")
            self.alg.write_log(app, "Validate extracted username %s" % username, "info")
            if username is None or username == '':
                self.alg.write_log(app, "username not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_USERNAME_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_USERNAME_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if not self.alg.check_param(credentials, 'password'):
                self.alg.write_log(app, "Password not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_PASSWORD_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_PASSWORD_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            password = str(credentials['password'])
            self.alg.write_log(app, "Extracted password ********", "info")
            self.alg.write_log(app, "Validate extracted password######", "info")
            if password is None or password == '':
                self.alg.write_log(app, "password not provided, return an error", "info")
                data['statusCode'] = StatusCodes.MISSING_PASSWORD_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_PASSWORD_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Authenticating user %s ..." % username, "info")
            """
            AUTH
            """
            auth = Auth(app, self.alg, username, password)
            auth_status = auth.is_authenticated()
            if auth_status is False:
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            csql = "SELECT c.clientID, c.clientName, u.status, c.status from users u inner join clients c on " \
                   "u.clientID=c.clientID where u.username='%s' AND u.userType='API'" % username
            cache_item = 'PROP%s%s' % (username, password)
            self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
            cdata = self.alg.retrieve_cached_data(cache_item)
            self.alg.write_log(app, "Redis SAYS -> %s" % cdata, "info")
            if cdata is None:
                cdata = self.connector.do_select(csql)
                self.alg.cache_data(cache_item, cdata)

            self.alg.write_log(app, "check auth => %s, sql => %s" % (str(cdata), csql), "info")
            status = cdata['status']
            if status == 'FAIL' or cdata['data'] is None:
                self.alg.write_log(app, "Authentication failed..Check client configurations", "info")
                data['statusCode'] = StatusCodes.AUTHENTICATION_FAILED
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.AUTHENTICATION_FAILED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            auth_data = cdata['data']
            parent_id = auth_data[0]
            user_status = auth_data[2]
            client_status = auth_data[3]

            if client_status == StatusCodes.INACTIVE:
                self.alg.write_log(app, "The client is not active", "info")
                data['statusCode'] = StatusCodes.INACTIVE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if user_status == StatusCodes.INACTIVE:
                self.alg.write_log(app, "The user is not active", "info")
                data['statusCode'] = StatusCodes.INACTIVE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INACTIVE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Username %s is authenticated, checking payload provided ..."
                               % username, "info")

            if not self.alg.check_param(json_req, 'packet'):
                self.alg.write_log(app, "Packet payload not specified ...", "info")
                data['statusCode'] = StatusCodes.MISSING_PACKET_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_PACKET_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            packet = json_req['packet']
            if packet is None:
                self.alg.write_log(app, "Packet payload not specified ...", "info")
                data['statusCode'] = StatusCodes.MISSING_PACKET_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_PACKET_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "validating packet %s ..." % packet, "info")
            '''
            Check and Extract the post parameters
            '''
            if not self.alg.check_param(packet, 'requestlogID'):
                data['statusCode'] = StatusCodes.MISSING_REQUESTLOGID_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_REQUESTLOGID_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                post_requestlog_id = packet['requestlogID']
                if post_requestlog_id == '':
                    data['statusCode'] = StatusCodes.MISSING_REQUESTLOGID_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_REQUESTLOGID_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp
            self.alg.write_log(app, "validated packet requestLogID param #####", "info")

            if not self.alg.check_param(packet, 'reference_number'):
                data['statusCode'] = StatusCodes.MISSING_REF_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_REF_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                post_ref_number = packet['reference_number']
                if post_ref_number == '':
                    data['statusCode'] = StatusCodes.MISSING_REF_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_REF_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp
            self.alg.write_log(app, "validated reference number####", "info")

            if not self.alg.check_param(packet, 'status_code'):
                data['statusCode'] = StatusCodes.MISSING_STATUS_CODE_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_STATUS_CODE_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                post_status_code = packet['status_code']
                if post_status_code == '':
                    data['statusCode'] = StatusCodes.MISSING_STATUS_CODE_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_STATUS_CODE_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp
            self.alg.write_log(app, "validated status code ####", "info")

            if not self.alg.check_param(packet, 'narration'):
                data['statusCode'] = StatusCodes.MISSING_NARRATION_PARAM
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.MISSING_NARRATION_PARAM)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            else:
                post_narration = packet['narration']
                if post_narration == '':
                    data['statusCode'] = StatusCodes.MISSING_NARRATION_VALUE
                    data['statusDescription'] = self.alg.get_status_description(app,
                                                                                StatusCodes.MISSING_NARRATION_VALUE)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp

            self.alg.write_log(app, "validated narration , processing ####", "info")

            '''
            Check the allowed status code
            '''
            try:
                post_status_code = int(post_status_code)
            except:
                data['statusCode'] = StatusCodes.INVALID_FINAL_STATUS_CODE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_FINAL_STATUS_CODE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if post_status_code != StatusCodes.PAYMENT_ACCEPTED and \
                            post_status_code != StatusCodes.PAYMENT_REJECTED and \
                            post_status_code != StatusCodes.MANUAL_RECON and \
                            post_status_code != StatusCodes.PAYMENT_IN_PROGRESS:
                data['statusCode'] = StatusCodes.INVALID_FINAL_STATUS_CODE
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.INVALID_FINAL_STATUS_CODE)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            '''
            Check whether the transaction exists and is not in the final status already
            '''
            check_sql = "SELECT t.transactionID, r.overalStatus,ccr.destinationClientID,ccr.notifyCustomer," \
                        "ccr.senderid ,r.source_account,ccr.channel_ref_id,ccr.callback FROM request_logs r inner join" \
                        " transactions t on r.requestlogID = t.requestlogID inner join " \
                        "client_channels_reference ccr on r.destination = ccr.code inner join clients c on " \
                        "ccr.clientID=c.clientID WHERE r.requestlogID = %d and r.external_ref_id = '%s'" \
                        % (post_requestlog_id, post_ref_number)

            self.alg.write_log(app, " sql => %s" % check_sql, "info")

            cdata = self.connector.do_select(check_sql)
            self.alg.write_log(app, "check transaction result => %s, sql => %s" % (str(cdata), check_sql), "info")

            status = cdata['status']
            tdata = cdata['data']
            if status == 'FAIL':
                self.alg.write_log(app, "Error during processing #####", "info")
                data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if tdata is None:
                self.alg.write_log(app, "Payment not found #####", "info")
                data['statusCode'] = StatusCodes.PAYMENT_NOT_FOUND
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.PAYMENT_NOT_FOUND)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            if tdata[0] is None:
                self.alg.write_log(app, "The payment does not exist using that combination. "
                                        "Check reference number and requestLogID", "info")
                data['statusCode'] = StatusCodes.PAYMENT_NOT_FOUND
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.PAYMENT_NOT_FOUND)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            '''
            Ensure that transaction being ack belong to this client, otherwise anyone can ack for anyone
            '''
            ownerID = int(tdata[2])
            self.alg.write_log(app, "Client authID is %d , transaction client OwnerID is %d..." % (parent_id, ownerID),
                               "info")
            '''
            check for override ID for payment router ack
            '''
            if parent_id != app.config['allowed_override_id']:
                self.alg.write_log(app, "Override not enforced for this client, id %d" % parent_id, "info")
                if parent_id != ownerID:
                    self.alg.write_log(app, "Authentication is to be done by whoever is accepting payment", "info")
                    data['statusCode'] = StatusCodes.ACK_CREDENTIAL_FAIL
                    data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.ACK_CREDENTIAL_FAIL)
                    resp = data
                    self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                    return resp
            else:
                self.alg.write_log(app, "Override enforced for this client, id %d" % parent_id, "info")

            try:
                final_status = int(tdata[1])
            except:
                self.alg.write_log(app, "Error during processing # Converting final status failed", "info")
                data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Validate is payment is in final status, db status %d..." % final_status, "info")

            if final_status == StatusCodes.PAYMENT_ACCEPTED or final_status == StatusCodes.PAYMENT_REJECTED or \
                            final_status == StatusCodes.MANUAL_RECON:
                data['statusCode'] = StatusCodes.PAYMENT_ALREADY_ACKNOWLEDGED
                data['statusDescription'] = self.alg.get_status_description(app,
                                                                            StatusCodes.PAYMENT_ALREADY_ACKNOWLEDGED)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            '''
            Update the payment to the final status
            '''
            upd_sql = "UPDATE request_logs SET overalStatus='%s' WHERE requestLogID=%d AND external_ref_id='%s'" \
                      % (post_status_code, post_requestlog_id, post_ref_number)

            self.alg.write_log(app, "Preparing update , query => %s" % upd_sql, "info")
            s_data = self.connector.do_update(upd_sql)

            if s_data['status'] == 'FAIL':
                self.alg.write_log(app, "Update request_logs failed. Try again or contact admin ###")
                data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp
            '''
            Update the transactions table
            '''
            upd_trx_sql = "UPDATE transactions SET destClientNarration='%s' WHERE requestLogID=%d" \
                          % (post_narration, post_requestlog_id)

            self.alg.write_log(app, "Preparing update , query => %s" % upd_trx_sql, "info")

            s_data = self.connector.do_update(upd_trx_sql)
            if s_data['status'] == 'FAIL':
                self.alg.write_log(app, "Update transactions failed. Try again or contact admin ###")
                data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
                data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
                resp = data
                self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
                return resp

            self.alg.write_log(app, "Checking if we should notify the customer ###", "info")
            '''
            Notify customer when transaction status changes
            '''
            notifyCustomer = tdata[3]
            self.alg.write_log(app, "notifyCustomer flag is %s ###" % str(notifyCustomer), "info")
            if str(notifyCustomer).lower() == 'yes':
                senderid = tdata[4]
                source_acc = tdata[5]
                self.alg.write_log(app, "senderid is %s , source_acc is %s ###" % (senderid, source_acc), "info")
                if senderid is not None and senderid is not '':
                    self.alg.write_log(app, "senderid is OK ###", "info")
                    if source_acc is not None and source_acc is not '':
                        self.alg.write_log(app, "source_acc is OK. Finding template... ###", "info")
                        '''
                        Get the appropriate template
                        '''
                        channel_ref_id = int(tdata[6])
                        check_msg_template_sql = "SELECT template from message_templates where channel_ref_id=%d and" \
                                                 " status_code_id=(select statusCodeID from statusCodes where " \
                                                 "code = '%s')" % (channel_ref_id, post_status_code)

                        self.alg.write_log(app, "Check template sql is %s ###" % check_msg_template_sql, "info")
                        cache_item = 'NOTI%d%s' % (channel_ref_id, post_status_code)
                        self.alg.write_log(app, "Get from redis first, KEY -> %s" % cache_item, "info")
                        noti_data = self.alg.retrieve_cached_data(cache_item)
                        self.alg.write_log(app, "Redis SAYS -> %s" % cdata, "info")
                        if noti_data is None:
                            noti_data = self.connector.do_select(csql)
                            self.alg.cache_data(cache_item, noti_data)

                        self.alg.write_log(app, "result is %s ###" % str(noti_data), "info")

                        if noti_data['data'] is None:
                            self.alg.write_log(app, "Template for status %s, channelref=> %d not found"
                                               % (post_status_code, channel_ref_id), "info")
                        else:
                            noti_bl = noti_data['data']
                            message = noti_bl[0]
                            '''
                            Update placeholders on the template
                            '''
                            message = self.alg.clean_message(app, message, post_requestlog_id)

                            self.alg.write_log(app, "Template found for status %s. Creating message ####"
                                               % post_status_code, "info")
                            ins_noti_sql = "INSERT INTO notifications (requestLogID, senderid, receiver,message," \
                                           "date_created,date_modified) VALUES (%d,'%s', '%s', '%s', now(), now())" \
                                           % (post_requestlog_id, senderid, source_acc, message)

                            self.alg.write_log(app, "notification query => %s" % ins_noti_sql, "info")
                            message_op = self.connector.do_insert(ins_noti_sql)
                            self.alg.write_log(app, "Ran insert query, result is %s" % str(message_op), "info")
                            if message_op is None:
                                self.alg.write_log(app, "Insert notification query failed. Notification might not be "
                                                        "sent", "info")
                            else:
                                self.alg.write_log(app, "Insert notification success. Push data { %s } to notifications"
                                                        " queue" % str(message_op), "info")
                                message_id = message_op['data']
                                if message_op['status'] != 'FAIL':
                                    message_data = {
                                        'messageid': message_id,
                                        'receiver': source_acc,
                                        'senderid': senderid,
                                        'message': message
                                    }
                                    self.alg.write_log(app, "Pushing notification to queue %s###" % str(message_data),
                                                       "info")
                                    st = self.alg.push_to_queue(app, app.config['notification_queue'], message_data)
                                    self.alg.write_log(app, "Notification results => %s " % st, "info")
                    else:
                        self.alg.write_log(app, "Can't send notification because source account was not found", "info")
                else:
                    self.alg.write_log(app, "Can't send notification because senderid was not found !", "info")
            '''
            if the channel has a callback URL, push the data to the call back queue, for external processing
            We care less at this point.
            '''
            self.alg.write_log(app, "Check if the channel has a callback for requestLogID %d" % post_requestlog_id,
                               "info")
            channel_callback_url = tdata[7]
            if channel_callback_url is not None:
                self.alg.write_log(app, "found call back => %s. Push to queue" % str(channel_callback_url), "info")
                if post_status_code == StatusCodes.PAYMENT_ACCEPTED:
                    final_status_code = 'SUCCESS'
                elif post_status_code == StatusCodes.PAYMENT_REJECTED:
                    final_status_code = 'FAIL'
                else:
                    final_status_code = 'UNKNOWN'
                callback_queue_data = {
                    'url': channel_callback_url,
                    'id': post_ref_number,
                    'status': final_status_code
                }
                st = self.alg.push_to_queue(app, app.config['callback_queue'], callback_queue_data)
                self.alg.write_log(app, "Push to queue result %s " % st, "info")

            self.alg.write_log(app, "send final status ####", "info")
            '''
            Return the final status
            '''
            data['statusCode'] = post_status_code
            data['statusDescription'] = self.alg.get_status_description(app, post_status_code)
            resp = data
            self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
            return resp
        except:
            error = str(sys.exc_info()[1])
            self.alg.write_log(app, "Error -> %s " % str(error), "error")
            data['statusCode'] = StatusCodes.GENERAL_SYSTEM_ERROR
            data['statusDescription'] = self.alg.get_status_description(app, StatusCodes.GENERAL_SYSTEM_ERROR)
            resp = data
            self.alg.write_log(app, "Response to be sent back %s..." % resp, "info")
            return resp


'''
Echo - Test up time for service
'''


class Echo(Resource):
    def __init__(self):
        # setup redis
        self.redis = RCache(app.config['redis_server'], app.config['redis_port'])
        # Setup database
        self.connector = Connector(app.config['db_server'], app.config['db_user'], app.config['db_password'],
                                   app.config['db_name'])
        # setup algorithms
        self.alg = PaymentAlgorithms(self.redis, self.connector)
        super(Echo, self).__init__()

    def get(self):
        return self.alg.run_echo_test()



'''
Documentation

Reference used below

http://flask-restful-cn.readthedocs.io/en/0.3.5/quickstart.html
'''
