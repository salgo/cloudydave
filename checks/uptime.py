from copy import copy
import subprocess
import traceback
import re


def test(cd, host, params):
    report = copy(cd.baseReport)
    report['test'] = 'uptime'
    result = {}

    try:
        proc = subprocess.Popen(['uptime'], stdout=subprocess.PIPE, close_fds=True)
        uptime = proc.communicate()[0]
        loadAvrgs = [res.replace(',', '.') for res in re.findall(r'([0-9]+[\.,]\d+)', uptime)]
        result = {'1': loadAvrgs[0], '5': loadAvrgs[1], '15': loadAvrgs[2], 'result': True}
    except Exception:
        print traceback.format_exc()
        result['result'] = False

    for key in result:
        report.update({'key': key, 'value': result[key]})
        cd.logResult(report)
