

class MongoDatastore(object):
    cd = False
    results = {}
    connection = False
    db = False

    def __init__(self, cd):
        self.cd = cd

        try:
            import pymongo
            self.connection = pymongo.Connection()
            self.db = self.connection.checks
        except ImportError:
            self.cd.log('mongo::ImportError', 'unable to import required '
                        'module pymongo')
            return False

    def log_result(self, host, check, result):
        result['date'] = self.cd.testdt

        if not host in self.results:
            self.results[host] = {}
        self.results[host][check] = result

    def save(self):
        for host in self.results:
            for check in self.results[host]:
                collection = self.db[host + ':' + check]
                collection.insert(self.results[host][check])
