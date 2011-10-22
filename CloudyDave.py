
import httplib, urllib2
import boto
from boto import sdb
from boto.sdb import SDBRegionInfo
from config import AWS_AccessKey, AWS_SecretKey, AWS_SDBDomainPrefix, AWS_SDBRegion, config
import pickle

class CloudyDave:
    
    region = None
    sdb = None
    configDomain = None
    cpickle = None
    
    def __init__(self):
        self.region = boto.sdb.get_region(AWS_SDBRegion)
        self.sdb = boto.connect_sdb(aws_access_key_id=AWS_AccessKey, aws_secret_access_key=AWS_SecretKey, region=self.region)

        if config:
            self.cpickle = pickle.dumps(config)

        self.config()
        
    def config(self):
        # Check to see if configuration is already SimpleDB
        
        if self.sdb.lookup(AWS_SDBDomainPrefix + '_config', True) == None:
            # Configuration isn't already in SimpleDB
            
            if cpickle == None:
                # Configuration isn't defined in the config file so can't rebuild
                raise Exception('config', 'no config defined')
            
            # Rebuild config
            self.setupConfig(config)
        else:
            # Otherwise get config domain
            self.configDomain = self.sdb.get_domain(AWS_SDBDomainPrefix + '_config')
            
            # Check config in SimpleDB is the same as config in config file
            pitems = self.configDomain.get_item('_configpickle')
            
            if not(pitems) or self.cpickle != pitems['data']:
                # If it isn't update config in SimpleDB
                self.setupConfig(config)

    def setupConfig(self, configDomain):
        # Add config to Simple DB for added cloudyness

        self.configDomain = self.sdb.create_domain(AWS_SDBDomainPrefix + '_config')

        if self.sdb.batch_put_attributes(self.configDomain, config) != True:
            return False
        
        self.configDomain.put_attributes('_configpickle', { 'data': self.cpickle })
        
        return True

    def runChecks(self):
        # Process uptime checks

        for item in self.configDomain:
            if item.name == '_configpickle' or not('services' in item):
                continue
            
            print item.name
            
            if isinstance(item['services'], (list, tuple)):
                for test_item in item['services']: 
                    print self.runTest(item.name, test_item)
            else:
                print self.runTest(item.name, item['services'])
    
    def runTest(self, host, test):
        testParams = test.split(':')

        test = testParams[0]	 
        del testParams[:1]

        if test == 'http':
           return self.httpTest(host, testParams)
        
        return None

    def httpTest(self, host, params):
        if len(params) == 0:
            params.append(80)
        if len(params) == 1:
            params.append(10)

        try:
            conn = httplib.HTTPConnection(host, params[0], params[1])
            conn.request('GET', '/', None, { 'User-Agent': 'Cloudy Dave' })
            response = conn.getresponse()
        
            if getattr(response, 'status') == 200:
                return True
        except:
            pass
       
        return False
