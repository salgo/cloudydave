"""print is a reference datastore that just prints out
the data it's given!!!"""


class DebugprintDatastore(object):
    results = {}

    def log_result(self, host, result):
        if not host in self.results:
            self.results[host] = []
        self.results[host].append(result)

    def save(self):

        for host in self.results:
            print "host:", host
            print self.results[host]
