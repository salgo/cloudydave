
checks = {'localhost': ['uptime',
                        {'check': 'mysqlstatus',
                         'user': 'root',
                         'password': 'lGrqTtrQVFjAs5uhW14t'}],
          'mx.littoralis.com': 'smtp',
          'andy-gale.com': 'http',
          'www.littoralis.com': {'check': 'http',
                                 'status': 200,
                                 'check_str': '<!-- super cache -->'},
          'secure.littoralis.com': 'https',
          'chef.salgo.net': {'check': 'http', 'port': 4040}}

datastores = {'debugprint': True}
