# Configuration 

AWS_AccessKey = ''
AWS_SecretKey = ''
AWS_SDBDomainPrefix = 'cloudydave'
AWS_SDBRegion = 'eu-west-1'

config = {'host.com': {'services': ['smtp', 'http', 'https']}}

# In our default config here... we're running tests on host.com
# The tests of host.com have to fail from two other hosts once
# before we get notified

# Tests from how many hosts have to fail before we get notified
NotifyOnHostFailures = 2

# How many failures causes notified
NotifyOnNumFailues = 1
