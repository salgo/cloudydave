
checks = {'localhost': ['uptime',
                        {'check': 'mysqlstatus',
                         'user': 'root',
                         'password': 'lGrqTtrQVFjAs5uhW14t'},
                        {'check': 'apachestatus',
                         'url': 'http://127.0.0.1/server-status?auto'}],
          'mx.littoralis.com': 'smtp',
          'andy-gale.com': 'http',
          'www.littoralis.com': {'check': 'http',
                                 'status': 200,
                                 'check_str': '<!-- super cache -->'},
          'secure.littoralis.com': 'https',
          'chef.salgo.net': {'check': 'http', 'port': 4040},
          'cloud.salgo.net': 'http'}

datastores = {'debugprint': True, 'mongo': True}
