# Configuration

AWS_AccessKey = '162XPEKGX9RABYZ4JTG2'
AWS_SecretKey = 'MmUsV08qb/9kyJPUIr7btjdcmk4TPlsMWCTlCJ+s'
AWS_SDBDomainPrefix = 'cloudydave'
AWS_SDBRegion = 'eu-west-1'
AWS_SDBRetryAttempts = 5


# Twilio Configuration

Twilio_AccountSID = 'ACb5d93479f7b945fa9cf7d538fb36c0c2'
Twilio_AuthToken = '3d1cbdfb0d37fffa38d16140eec32eae'
Twilio_SendNumber = '+442033222732'
Twilio_RetryAttempts = 5

# Pushover configuration
Pushover_APIKey = 'bIiRyB8dg7EPCli2oxZpAuHTyyVNml'


config = {
          'localhost': [{'test': 'apachestatus', 'url': 'http://localhost/server-status?auto'},
                        'uptime',
                        {'test': 'mysqlstatus', 'user': 'root', 'password': 'lGrqTtrQVFjAs5uhW14t'}],

          # 'www.littoralis.com': 'http',
          # 'secure.littoralis.com': ['https'],
          'mx.littoralis.com': ['smtp'],
          # 'andy-gale.com': ['http'],
          # 'chef.salgo.net': [{'test': 'http', 'port': 4040}, {'test': 'http', 'port': 4000}],
          # 'starbuck.salgo.net': ['http'],
          # 'localhost': ['http', {'test': 'mysql-status', 'user': 'root', 'password': ''}, 'uptime']
          }

#NotifyOnHostFailures = 2
#NotifyOnNumFailues = 1

andysmobile_number = "+447825661580"

# Things we want to be notified about.

notify = {'starbuck.salgo.net': [{'test': 'http',
                                  'key': 'result',
                                  'cmp': '=',
                                  'value': "False",
                                  'notify-number': andysmobile_number,
                                  'message': "down"
                                  }],
          'lightening.littoralis.com': [{'test': 'uptime',
                                         'testhost': 'localhost',
                                         'key': '1',
                                         'cmp': '>',
                                         'value': 8,
                                         'notify-number': andysmobile_number,
                                         'message': 'load average above 8'
                                        }],
          'www.littoralis.com': [{'test': 'http',
                                  'key': 'result',
                                  'cmp': '=',
                                  'value': "False",
                                  'notify-number': andysmobile_number,
                                  'message': "down"
                                  }],
          'secure.littoralis.com': [{'test': 'https',
                                     'key': 'result',
                                     'cmp': '=',
                                     'value': "False",
                                     'notify-number': andysmobile_number,
                                     'message': "down"
                                    }],
          'mx.littoralis.com': [{'test': 'smtp',
                                 'key': 'result',
                                 'cmp': '=',
                                 'value': "False",
                                 'notify-number': andysmobile_number,
                                 'message': "down"
                                }],
          'andy-gale.com': [{'test': 'http',
                             'key': 'result',
                             'cmp': '=',
                             'value': "False",
                             'notify-number': andysmobile_number,
                             'message': "down"
                            }],
          'chef.salgo.net': [{'test': 'http:4000',
                              'key': 'result',
                              'cmp': '=',
                              'value': "False",
                              'notify-number': andysmobile_number,
                              'message': "down",
                              'service': "Chef server"
                            },
                            {'test': 'http:4040',
                              'key': 'result',
                              'cmp': '=',
                              'value': "False",
                              'notify-number': andysmobile_number,
                              'message': "down",
                              'service': "Chef web gui"
                             }]}
