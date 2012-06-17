import smtplib
from copy import copy


class SmtpCheck(object):
    def test(self, cd, host, params):
        report = copy(cd.basereport)

        check = 'smtp'

        if not('port' in params):
            params['port'] = 25
        else:
            check += ':' + unicode(params['port'])

        if not('timeout' in params):
            params['timeout'] = 10

        try:
            server = smtplib.SMTP(host, params['port'], cd.hostname,
                                  params['timeout'])
            server.helo(cd.hostname)
            server.quit()
            report['result'] = True
        except:
            report['result'] = False

        cd.log_result(host, check, report)

        return report['result']
