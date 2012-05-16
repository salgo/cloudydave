import httplib
import boto
from boto import sdb
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBRegion, config
import smtplib
import socket
from datetime import datetime
from datetime import timedelta
from copy import copy
import time
import subprocess
import traceback
import re


class CloudyDave:

    region = None
    sdb = None
    hostname = None
    logDomain = None
    testDateTime = None
    testDateTimeEpoc = None

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
            else:
                self.runTest(host, item)

    def runTest(self, host, test, params=None):
        if params is None:
            params = {}

        if test == 'http':
            result = self.httpTest(host, params)
        elif test == 'https':
            result = self.httpTest(host, params, True)
        elif test == 'smtp':
            result = self.smtpTest(host, params)
        elif test == 'mysql-status':
            result = self.mysqlStatusTest(host, params)
        elif test == 'uptime':
            result = self.uptimeTest()
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

    def smtpTest(self, host, params):

        report = copy(self.baseReport)
        report['key'] = 'result'
        report['test'] = 'smtp'

        if not('port' in params):
            params['port'] = 25
        else:
            report['test'] += ':' + unicode(params['port'])

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            server = smtplib.SMTP(host, params['port'], self.hostname, params['timeout'])
            server.helo(self.hostname)
            server.quit()

            report['value'] = True

        except:
            report['value'] = False

        self.logResult(report)

    def mysqlStatusTest(self, host, params):

        report = copy(self.baseReport)
        report['test'] = 'mysql-status'
        result = {}

        if not('port' in params):
            params['port'] = 3306

            try:
                import MySQLdb
                try:
                    db = MySQLdb.connect(host=host,
                                         user=params['user'],
                                         passwd=params['password'])
                    cursor = db.cursor()
                    cursor.execute("SHOW GLOBAL STATUS")
                    tresult = cursor.fetchall()

                    stats = ['Created_tmp_disk_tables', 'Connections',
                             'Max_used_connections', 'Open_files',
                             'Slow_queries', 'Table_locks_waited',
                             'Threads_connected']

                    for stat in tresult:
                        if stat[0] in stats:
                            result[stat[0]] = stat[1]

                    result['result'] = True

                except MySQLdb.OperationalError:
                    result['result'] = False

            except ImportError:
                result['result'] = False

        for key in result:
            report.update({'key': key, 'value': result[key]})
            self.logResult(report)

    def uptimeTest(self):
        report = copy(self.baseReport)
        report['test'] = 'uptime'
        result = {}

        try:
            proc = subprocess.Popen(['uptime'], stdout=subprocess.PIPE, close_fds=True)
            uptime = proc.communicate()[0]
            loadAvrgs = [res.replace(',', '.') for res in re.findall(r'([0-9]+[\.,]\d+)', uptime)]
            result = {'1': loadAvrgs[0], '5': loadAvrgs[1], '15': loadAvrgs[2], 'result': True}
        except Exception:
            print traceback.format_exc()
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

        timestamp = " timestamp >= '" + startdt.strftime("%s") + \
                    "' AND timestamp <= '" + enddt.strftime("%s") + "'"

        query = "SELECT * FROM " + domain.name + " WHERE " + where + timestamp + ' ORDER BY timestamp'

        rs = domain.select(query)

        data = []

        for item in rs:
            dt = datetime.fromtimestamp(int(item['timestamp']))
            date = dt.strftime("%s")
            data.append([date, item['value']])

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
