from copy import copy
import subprocess
import traceback
import re


class UptimeCheck(object):
    def test(self, cd, host, params):
        report = copy(cd.basereport)
        report['check'] = 'uptime'

        resultBool = False

        try:
            proc = subprocess.Popen(['uptime'],
                                    stdout=subprocess.PIPE,
                                    close_fds=True)
            uptime = proc.communicate()[0]
            loadavrgs = [res.replace(',', '.')
                for res in re.findall(r'([0-9]+[\.,]\d+)', uptime)]
            report.update({'1': loadavrgs[0],
                           '5': loadavrgs[1],
                           '15': loadavrgs[2]})
            resultBool = True
        except Exception:
            print traceback.format_exc()
            report['result'] = False

        cd.log_result(host, report)

        return resultBool
