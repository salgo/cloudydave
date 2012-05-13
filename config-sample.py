# Configuration

# AWS Configuration
AWS_AccessKey = ''
AWS_SecretKey = ''
AWS_SDBDomainPrefix = ''
AWS_SDBRegion = ''

# Twilio Configuration
Twilio_AccountSID = ''
Twilio_AuthToken = ''
Twilio_SendNumber = ''

# Things to test, data to store
config = {'www.example1.com': 'http',
          'www.example2.com': ['https'],
          'www.example3.com': ['http', 'https'],
          'mx.example4.com': ['smtp'],
          'www.example5.com': [{'test': 'http', 'port': 4040}],
          'localhost': ['http', {'test': 'mysql-status', 'user': 'root', 'password': ''}, 'uptime']
}

# Tests from how many hosts have to fail before we get notified
NotifyOnHostFailures = 2

# How many failures causes notified
NotifyOnNumFailues = 1

# Things to notify us about - notice result should be a string as that's
# the only data type stored in the back end
notify = {'www.example1.com': [{'test': 'http',
                                'key': 'result',
                                'value': 'False',
                                'notify-failure': True,
                                'notify-recovery': True,
                                'notify-number': '+441818118181',
                                'notify-email': 'alerts@example.com'}]}
