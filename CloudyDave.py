
import httplib, urllib2
import boto
from boto import sdb
from boto.sdb import SDBRegionInfo
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBDomainPrefix, AWS_SDBRegion, config, NotifyOnHostFailures, NotifyOnNumFailues
from httplib import HTTPSConnection
import smtplib
import socket

class CloudyDave:
    
    region = None
    sdb = None
    hostname = None
    
    def __init__(self):
        self.region = boto.sdb.get_region(AWS_SDBRegion)
        self.sdb = boto.connect_sdb(aws_access_key_id=AWS_AccessKey, aws_secret_access_key=AWS_SecretKey, region=self.region)
        self.hostname = socket.gethostname()

    def runChecks(self):
        # Process uptime checks
        
        for host in config:
            item = config[host]

            # If there's more than one test it's an array
            
            if isinstance(item['services'], (list, tuple)):
                for test_item in item['services']: 
                    self.runTest(host, test_item)
            else:
                # If there's only one test defined it might be a string
                self.runTest(host, item['services'])
    
    def runTest(self, host, test):
        testParams = test.split(':')

        test = testParams[0]	 
        del testParams[:1]

        if test == 'http':
            result = self.httpTest(host, testParams)
        elif test == 'https':
            result = self.httpsTest(host, testParams)
        elif test == 'smtp': 
            result = self.smtpTest(host, testParams)
        else:
            print "Don't know how to test '" + test + "'"
            result = None
        
        self.logResult(host, test, testParams, result)
        
        return result

    def logResult(self, host, test, params, result):
        
        print host + ": " + test + ": " + str(params) + ": " + str(result)
        

    def httpTest(self, host, params):
        if len(params) == 0:
            params.append(80)
        if len(params) == 1:
            params.append(10)

        try:
            conn = httplib.HTTPConnection(host, params[0], params[1])
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
            
            status = getattr(response, 'status')
        
            if status == 200 or status == 301 or status == 302:
                return True
        except:
            pass
       
        return False
        
    def httpsTest(self, host, params):
        if len(params) == 0:
            params.append(443)
        if len(params) == 1:
            params.append(10)

        try:
            conn = httplib.HTTPSConnection(host, params[0], None, None, None, params[1])
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
            
            status = getattr(response, 'status')
        
            if status == 200 or status == 301 or status == 302:
                return True
        except:
            pass    
                
        return False

    def smtpTest(self, host, params): 
        
        if len(params) == 0:
            params.append(25)
        if len(params) == 1:
            params.append(10)
        
        try:        
            server = smtplib.SMTP(host, params[0], self.hostname, params[1])
            server.helo(self.hostname)
            server.quit()
            
            return True
        
        except:
            
            pass
        
        return False