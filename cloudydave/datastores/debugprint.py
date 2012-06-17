"""print is a reference datastore that just prints out
the data it's given!!!"""


class DebugprintDatastore(object):
    results = {}

    def log_result(self, host, check, result):
        if not host in self.results:
            self.results[host] = {}
        self.results[host][check] = result

    def save(self):
        for host in self.results:
            print "host:", host
            for check in self.results[host]:
                print "check:", check
                print self.results[host][check]
