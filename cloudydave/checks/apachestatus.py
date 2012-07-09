from copy import copy


class ApachestatusCheck(object):
    def test(self, cd, host, params):
        report = copy(cd.basereport)

        try:
            import urllib
        except ImportError:
            cd.log('apachestatus::ImportError', 'unable to import required '
                   'module httplib')

        check = 'apachestatus'

        f = urllib.urlopen(params['url'])
        to_parse = f.read()

        lines = to_parse.split('\n')
        apacheData = {}

        for line in lines:
            tdata = line.split(': ')

            if len(tdata) > 1:
                apacheData[str(tdata[0])] = tdata[1]

        if 'Total Accesses' in apacheData:
            report['totalaccesses'] = float(apacheData['Total Accesses'])

        if 'ReqPerSec' in apacheData:
            report['reqpersec'] = float(apacheData['ReqPerSec'])

        if 'BytesPerSec' in apacheData:
            report['bytespersec'] = float(apacheData['BytesPerSec'])

        if 'BytesPerReq' in apacheData:
            report['bytesperreq'] = float(apacheData['BytesPerReq'])

        if 'BusyWorkers' in apacheData:
            report['busyworkers'] = float(apacheData['BusyWorkers'])

        if 'IdleWorkers' in apacheData:
            report['IdleWorkers'] = float(apacheData['IdleWorkers'])

        cd.log_result(host, check, report)

        #return report['result']

        return True
