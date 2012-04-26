
import httplib, urllib2
import boto
from boto import sdb
from boto.sdb import SDBRegionInfo
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBDomainPrefix, AWS_SDBRegion, config, NotifyOnHostFailures, NotifyOnNumFailues
from httplib import HTTPSConnection
import smtplib
import socket
import datetime

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

    def runChecks(self):
        # Process uptime checks
        for host in config:
            item = config[host]
            
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
            result = self.httpsTest(host, params)
        elif test == 'smtp': 
            result = self.smtpTest(host, params)
        else:
            print "Don't know how to test '" + test + "'"
            result = None
        
        self.logResult(host, test, params, result)
        
        return result

    def logResult(self, host, test, params, result):
        
        print "logResult:" + host + ": " + test + ": " + str(params) + ": " + str(result)  
        
        key = [ self.hostname, self.testDateTimeEpoc, host] 
            
        string_params = []

        for item in params:
            key.append(item + ':' + str(params[item]))
            string_params.append(item + ':' + str(params[item]))
        
        tkey = '/'.join(key)
        
        print tkey
        
        item = { 'fromhost': self.hostname,
                 'timestamp': self.testDateTimeEpoc,
                 'params': ':'.join(string_params), 
                 'testhost': host, 
                 'test': test,
                 'result': result }
        
        if not(self.sdb.logDomain.put_attributes(tkey, item)):
            print "Unable to save results!"
    
    def getDomain(self):
        return self.sdb.logDomain

    def httpTest(self, host, params):

        if not('port' in params):
            params['port'] = 80

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            conn = httplib.HTTPConnection(host, params['port'], params['timeout'])
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
            
            status = getattr(response, 'status')
        
            if status == 200 or status == 301 or status == 302:
                return True
        except:
            pass
       
        return False
        
    def httpsTest(self, host, params):
        if not('port' in params):
            params['port'] = 443

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            conn = httplib.HTTPSConnection(host, params['port'], None, None, None, params['timeout'])
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
            
            status = getattr(response, 'status')
        
            if status == 200 or status == 301 or status == 302:
                return True
        except:
            pass    
                
        return False

    def smtpTest(self, host, params): 
        
        if not('port' in params):
            params['port'] = 25

        if not('timeout' in params):
            params['timeout'] = 10
        
        try:        
            server = smtplib.SMTP(host, params['port'], self.hostname, params['timeout'])
            server.helo(self.hostname)
            server.quit()
            
            return True
        
        except:
            
            pass
        
        return False