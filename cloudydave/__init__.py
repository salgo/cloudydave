# -*- coding: utf-8 -*-
import socket
from datetime import datetime


checkmodules = None
try:
    from cloudydave.checks import __all__ as checkmodules
    from cloudydave.checks import *
except ImportError:
    pass


class cloudydave:
    hostname = None
    testdt = None
    testdtepoc = None
    checks = None
    datastores = None
    checkmodules = None

    def __init__(self, checks):
        self.hostname = socket.gethostname()
        self.testdt = datetime.utcnow()
        self.testdtepoc = self.testdt.strftime("%s")
        self.checks = checks

        # Load check modules
        try:
            self.checkmodules = checkmodules
        except ImportError:
            pass

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

    def log_result(self, report):
        print report
