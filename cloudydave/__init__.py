# -*- coding: utf-8 -*-
import socket
from datetime import datetime


checkmodules = None
try:
    from cloudydave.checks import __all__ as checkmodules
    from cloudydave.checks import *
except ImportError:
    pass

datastoremodules = None
try:
    from cloudydave.datastores import __all__ as datastoremodules
    from cloudydave.datastores import *
except ImportError:
    pass


class cloudydave:
    hostname = None
    testdt = None
    testdtepoc = None
    checks = None
    datastores = None
    checkmodules = None

    def __init__(self, checks, datastores):
        self.hostname = socket.gethostname()
        self.testdt = datetime.utcnow()
        self.testdtepoc = self.testdt.strftime("%s")
        self.checks = checks
        self.datastores = datastores

        # Load check modules
        self.checkmodules = checkmodules
        self.datastoremodules = datastoremodules
        self.ds = {}

        for datastore in datastores:
            if datastore in self.datastoremodules:
                self.ds[datastore] = eval(datastore + '.' +
                                          datastore.capitalize() +
                                          'Datastore()')

    def log(self, msg):
        print "cloudydave::log:", msg

    def run_checks(self):
        """Parse various config formats and call each check"""

        for host in self.checks:
            item = self.checks[host]

            if host == 'localhost':
                # No need to store it's localhost as the test host,
                # that's assumed
                self.basereport = {}
            else:
                self.basereport = {'testhost': host}

            if isinstance(item, list):
                for check in item:
                    if isinstance(check, (dict)):
                        self.run_check(host, check['check'], check)
                    else:
                        self.run_check(host, check)
            elif isinstance(item, (dict)):
                self.run_check(host, item['check'], item)
            else:
                self.run_check(host, item)

        self.save_result()

    def run_check(self, host, check, params=None):
        if params is None:
            params = {}

        if check in self.checkmodules:
            checkmodule = eval(check + '.' + check.capitalize() + 'Check()')
            result = checkmodule.test(self, host, params)
        else:
            print "Don't know how to check '" + check + "'"
            result = None

        return result

    def log_result(self, host, report):
        for ds in self.ds:
            self.ds[ds].log_result(host, report)

    def save_result(self):
        for ds in self.ds:
            self.ds[ds].save()
