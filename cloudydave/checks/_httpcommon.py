from copy import copy
import time


def httpcheck(cd, host, params, secure=False):
    try:
        import httplib
    except ImportError:
        cd.log('http::ImportError', 'unable to import required '
               'module httplib')
        return False

    report = copy(cd.basereport)
    result = {}

    if secure:
        report['check'] = 'https'
    else:
        report['check'] = 'http'

    if not('port' in params):
        if secure:
            params['port'] = 443
        else:
            params['port'] = 80
    else:
        report['check'] += ':' + unicode(params['port'])

    if not('timeout' in params):
        params['timeout'] = 10

    try:
        start = time.time()

        if secure:
            conn = httplib.HTTPSConnection(host, params['port'],
                            None, None, None, params['timeout'])
        else:
            conn = httplib.HTTPConnection(host, params['port'],
                                          params['timeout'])

        conn.request('GET', '/', None, {'User-Agent': 'Cloudy Dave'})
        response = conn.getresponse()
        data = response.read()

        status = getattr(response, 'status')

        report['response_time'] = time.time() - start
        report['status'] = status

        if ('status' in params and status == params['status']) or\
           (status == 200 or status == 301 or status == 302):
            if 'check_str' in params:
                if params['check_str'] in data:
                    report['check_str'] = True
                else:
                    report['check_str'] = False
            report['result'] = True

    except:
        report['result'] = False

    cd.log_result(host, report)

    return report['result']
