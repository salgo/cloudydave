
import httplib, urllib2
import boto
from boto import sdb
from boto.sdb import SDBRegionInfo
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBDomainPrefix, AWS_SDBRegion, config, NotifyOnHostFailures, NotifyOnNumFailues
from httplib import HTTPSConnection
import smtplib
import socket
import datetime
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
                        
        self.testDateTime = datetime.datetime.utcnow()
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
    
    def runTest(self, host, test, params = None):
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
        
    # def logResult(self, host, test, params, result):
    #             
    #     key = [ self.hostname, self.testDateTimeEpoc, host] 
    #         
    #     string_params = []
    # 
    #     if 'host' in params:
    #         del params['host']
    # 
    #     for item in params:
    #         if item == 'password':
    #             continue
    #         key.append(item + ':' + str(params[item]))
    #         string_params.append(item + ':' + str(params[item]))
    #     
    #     tkey = '/'.join(key)
    #     
    #     print tkey, result
    #     
    #     if isinstance(result, (dict)):
    #         
    #         for k in result:
    #             ttkey = tkey + '/' + k
    #             item = { 'fromhost': self.hostname,
    #                      'timestamp': self.testDateTimeEpoc,
    #                      'params': ':'.join(string_params), 
    #                      'testhost': host, 
    #                      'test': test,
    #                      'testKey': k,
    #                      'result': result[k] }
    #             self._logResult(ttkey, item)
    #     else:
    #         item = { 'fromhost': self.hostname,
    #                  'timestamp': self.testDateTimeEpoc,
    #                  'params': ':'.join(string_params), 
    #                  'testhost': host, 
    #                  'test': test,
    #                  'result': result }
    #                  
    #         self._logResult(tkey, item)
    
    def logResult(self, item):
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
                
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
            data = response.read()
            ttlb = time.time() - start
            
            status = getattr(response, 'status')
            
            result['response_time'] = time.time() - start
            result['status'] = status
                
            if status == 200 or status == 301 or status == 302:
                if 'checkStr' in params:
                    if parms['checkStr'] in data:
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
				# Connect
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
                    
                    ret = {}
                    
                    for stat in tresult:
                        if stat[0] in stats:
                            result[stat[0]] = stat[1]
                    
                    result['result'] = True
                    
                except MySQLdb.OperationalError, message:
                    result['result'] = False

            except ImportError, e:
                results['result'] = False

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
        except Exception, e:
            print traceback.format_exc()
            result['result'] = False
        
        for key in result:
            report.update({'key': key, 'value': result[key]})
            self.logResult(report)