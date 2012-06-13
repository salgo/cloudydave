import smtplib
from copy import copy


class SmtpCheck(object):
    def test(self, cd, host, params):
        report = copy(cd.basereport)
        report['key'] = 'result'
        report['test'] = 'smtp'

        if not('port' in params):
            params['port'] = 25
        else:
            report['test'] += ':' + unicode(params['port'])

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            server = smtplib.SMTP(host, params['port'], cd.hostname,
                                  params['timeout'])
            server.helo(cd.hostname)
            server.quit()
            report['value'] = True
        except:
            report['value'] = False

        cd.log_result(report)

        return report['value']
