from __future__ import division

import httplib
import boto
from boto import sdb
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBRegion, config, AWS_SDBRetryAttempts
from config import Twilio_AccountSID
from config import Twilio_AuthToken
from config import Twilio_SendNumber
from config import Twilio_RetryAttempts
import socket
from datetime import datetime
from datetime import timedelta
from copy import copy
import time


from twilio.rest import TwilioRestClient


# Useful when one is testing :)
DO_NOT_SEND_TEXTS = False

try:
    checkmodules_available = True
    from checks import *
    from checks import __all__ as checkModules
except ImportError:
    checkmodules_available = False


class CloudyDave:

    region = None
    sdb = None
    hostname = None
    logDomain = None
    testDateTime = None
    testDateTimeEpoc = None
    checkModules = None

    def __init__(self):
        self.region = boto.sdb.get_region(AWS_SDBRegion)
        self.sdb = boto.connect_sdb(aws_access_key_id=AWS_AccessKey, aws_secret_access_key=AWS_SecretKey, region=self.region)
        self.hostname = socket.gethostname()

        if self.sdb.lookup('tests', True) == None:
            self.sdb.create_domain('tests')
        else:
            self.sdb.logDomain = self.sdb.get_domain('tests')

        self.testDateTime = datetime.utcnow()
        self.testDateTimeEpoc = self.testDateTime.strftime("%s")

        self.baseReport = {'fromhost': self.hostname,
                           'timestamp': self.testDateTimeEpoc}

        self.checkModules = self.registerCheckModules()

    def registerCheckModules(self):
        if checkmodules_available:
            return checkModules
        else:
            return []

    def log(self, level, msg):
        print level, msg

    def runChecks(self):
        # Process uptime checks
        for host in config:
            item = config[host]

            self.baseReport.update({'testhost': host})

            if isinstance(item, list):
                for test in item:
                    if isinstance(test, (dict)):
                        self.runTest(host, test['test'], test)
                    else:
                        self.runTest(host, test)
            elif isinstance(item, (dict)):
                self.runTest(host, item['test'], item)
            else:
                self.runTest(host, item)

    def runTest(self, host, test, params=None):
        if params is None:
            params = {}

        if test == 'http':
            result = self.httpTest(host, params)
        elif test == 'https':
            result = self.httpTest(host, params, True)
        elif test in self.checkModules:
            checktest = eval(test)
            result = checktest.test(self, host, params)
        else:
            print "Don't know how to test '" + test + "'"
            result = None

        return result

    def logResult(self, item):

        if item['testhost'] == 'localhost':
            item['testhost'] = item['fromhost']

        tkey = []
        for key in item:
            tkey.append(key + ':' + unicode(item[key]))
        tkey = '/'.join(tkey)

        if not(self.sdb.logDomain.put_attributes(tkey, item)):
            print "Unable to save results!"

    def getDomain(self):
        return self.sdb.logDomain

    def httpTest(self, host, params, secure=False):

        report = copy(self.baseReport)
        result = {}

        if secure:
            report['test'] = 'https'
        else:
            report['test'] = 'http'

        if not('port' in params):
            if secure:
                params['port'] = 443
            else:
                params['port'] = 80
        else:
            report['test'] += ':' + unicode(params['port'])

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            start = time.time()

            if secure:
                conn = httplib.HTTPSConnection(host, params['port'], None, None, None, params['timeout'])
            else:
                conn = httplib.HTTPConnection(host, params['port'], params['timeout'])

            conn.request('GET', '/', None, {'User-Agent': 'Cloudy Dave'})
            response = conn.getresponse()
            data = response.read()

            status = getattr(response, 'status')

            result['response_time'] = time.time() - start
            result['status'] = status

            if status == 200 or status == 301 or status == 302:
                if 'checkStr' in params:
                    if params['checkStr'] in data:
                        result['result'] = True
                    else:
                        result['result'] = False
                else:
                    result['result'] = True

        except:
            result['result'] = False

        for key in result:
            report.update({'key': key, 'value': result[key]})
            self.logResult(report)

    def commandArgs(self, args):
        query = ""
        limit = None
        datefrom = False
        dateto = False

        args.pop(0)

        while len(args) > 1:
            key = args.pop(0)
            eq = args.pop(0)

            if key == 'limit':
                limit = int(eq)
                continue

            if key == 'datetime':
                datefrom = eq + ' ' + args.pop(0)
                dateto = args.pop(0) + ' ' + args.pop(0)
                continue

            value = args.pop(0)

            query += ' AND ' + key + ' ' + eq + " '" + value + "'"

        if datefrom and dateto:
            timestamp_start = datetime.strptime(datefrom, "%Y-%m-%d %H:%M:%S")
            timestamp_end = datetime.strptime(dateto, "%Y-%m-%d %H:%M:%S")
            timestamp = " timestamp >= '" + timestamp_start.strftime("%s") + \
                        "' AND timestamp <= '" + timestamp_end.strftime("%s") + "'"
        else:
            timestamp = " timestamp > '0'"

        return timestamp + query, limit

    def reportAgo(self, seconds_ago=120):
        """Get list of available results in the last seconds_ago seconds"""
        nowdt = datetime.utcnow()
        beforedt = nowdt - timedelta(seconds=seconds_ago)
        return self.report(beforedt, nowdt)

    def report(self, startdt, enddt):
        """Get list of available results in between the startdt and enddt"""

        domain = self.sdb.logDomain

        timestamp = " timestamp >= '" + startdt.strftime("%s") + \
                    "' AND timestamp <= '" + enddt.strftime("%s") + "'"

        query = "SELECT * FROM " + domain.name + " WHERE " + timestamp

        rs = domain.select(query)

        uniques = {}
        unique_fields = ['fromhost', 'testhost', 'test', ('test', 'key')]

        for item in rs:

            for field in unique_fields:
                if isinstance(field, tuple):
                    key = field[0] + '/' + field[1]
                else:
                    key = field

                if not(key in uniques):
                    uniques[key] = []

                if isinstance(field, tuple):

                    value = item[field[0]] + '/' + item[field[1]]
                else:
                    value = item[field]

                if not(value in uniques[key]):
                    uniques[key].append(value)

        return uniques

    def graphQuery(self, startdt, enddt, **kwargs):
        """Perform query for graphing"""

        domain = self.sdb.logDomain

        where = ''

        for kwarg in kwargs:
            where += "{} = '{}' AND ".format(kwarg, kwargs[kwarg])

        data_is_difference = False

        if 'test' in kwargs and 'key' in kwargs:
            if kwargs['test'] == 'mysql-status' and kwargs['key'] == 'Connections':
                data_is_difference = True

        timestamp = " timestamp >= '" + startdt.strftime("%s") + \
                    "' AND timestamp <= '" + enddt.strftime("%s") + "'"

        query = "SELECT * FROM " + domain.name + " WHERE " + where + timestamp + ' ORDER BY timestamp'

        rs = domain.select(query)

        data = []

        previous = None
        for item in rs:
            if data_is_difference:
                if previous is None:
                    # Need a difference so can't show the first match
                    previous = float(item['value'])
                    continue
                else:
                    fval = float(item['value'])
                    value = (fval - previous) / 60
                    if value < 0:
                        value = 0
                    previous = fval
            else:
                value = item['value']

            dt = datetime.fromtimestamp(int(item['timestamp']))
            date = dt.strftime("%s")

            data.append([date, value])

        return data

    def notifyInit(self):
        """Assuming most clients don't want to use notify so don't init unless
        we have to"""

        if self.sdb.lookup('notify', True) == None:
            self.sdb.create_domain('notify')

        self.notifyDomain = self.sdb.get_domain('notify')

    def notifyKey(self, testhost, notify):
        nnkeya = [testhost]

        for key in ['testhost', 'test', 'key', 'cmp', 'value']:
            if key in notify:
                nnkeya.append(unicode(notify[key]))

        return '/'.join(nnkeya)

    def notifyStatus(self, testhost, notify, failed):

        nnkey = self.notifyKey(testhost, notify)

        data = self.notifyDomain.get_item(nnkey)

        if failed:
            if data:
                return False
            else:
                item = self.notifyDomain.new_item(nnkey)
                item['a'] = True
                item.save()
                return True
        else:
            if data:
                data.delete()
                return True
            else:
                return False

    def notifyCheck(self, testhost, test):
        """Process notification checks and send SMS, emails and whatever else if they are required"""

        domain = self.getDomain()

        query = "SELECT * FROM {} WHERE timestamp > '0' AND ".format(domain.name)

        if 'testhost' in test:
            # As test host is specified the host specified in the notify is actually the fromhost
            query += " fromhost = '{}' AND testhost = '{}'".format(testhost, test['testhost'])
        else:
            query += "testhost = '{}'".format(testhost)

        query += " AND test = '{}' AND key = '{}' ORDER BY timestamp DESC".format(test['test'], test['key'])

        rs = domain.select(query, max_items=1)

        retries = 0

        failed = False

        while retries < AWS_SDBRetryAttempts:
            try:
                for item in rs:
                    if not('cmp' in test) or test['cmp'] == '=':
                        if item['value'] == test['value']:
                            failed = True
                    else:
                        # number compares
                        test_value = float(test['value'])
                        actual_value = float(item['value'])

                        if test['cmp'] == '>':
                            if actual_value > test_value:
                                failed = True
                        elif test['cmp'] == '>=':
                            if actual_value >= test_value:
                                failed = True
                        elif test['cmp'] == '<':
                            if actual_value < test_value:
                                failed = True
                        elif test['cmp'] == '<=':
                            if actual_value <= test_value:
                                failed = True
                break
            except boto.exception.SDBResponseError:
                time.sleep(1)
                retries += 1

        if retries == AWS_SDBRetryAttempts:
            print "SBD timeout after", AWS_SDBRetryAttempts, "attempts"
            return

        send_notify = self.notifyStatus(testhost, test, failed)
        if send_notify:

            if failed:
                if 'message' in test:
                    msg = test['message']
                else:
                    msg = 'failed'
            else:
                msg = 'recovered'

            if 'service' in test:
                service = test['service']
            else:
                service = test['test']

            body = "{} on {}: {}".format(service, testhost, msg)

            if not(DO_NOT_SEND_TEXTS):
                retries = 0
                while retries < Twilio_RetryAttempts:
                    try:
                        print "attempting to send", Twilio_SendNumber, body
                        client = TwilioRestClient(Twilio_AccountSID, Twilio_AuthToken)
                        client.sms.messages.create(to=test['notify-number'],
                                                   from_=Twilio_SendNumber,
                                                   body=body)
                        break
                    except Exception:
                        # print "TwilioRestClient timeout", retries
                        retries += 1
                        time.sleep(1)

                if retries == Twilio_RetryAttempts:
                    print "Unable to send SMS after", Twilio_RetryAttempts, "attempts"

            print body
