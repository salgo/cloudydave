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
        report['test'] = 'https'
    else:
        report['test'] = 'http'

    if not('port' in params):
        if secure:
            params['port'] = 443
        else:
            params['port'] = 80
    else:
        report['test'] += ':' + unicode(params['port'])

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

        result['response_time'] = time.time() - start
        result['status'] = status

        if status == 200 or status == 301 or status == 302:
            if 'checkStr' in params:
                if params['checkStr'] in data:
                    result['result'] = True
                else:
                    result['result'] = False
            else:
                result['result'] = True

    except:
        result['result'] = False

    for key in result:
        report.update({'key': key, 'value': result[key]})
        cd.log_result(report)

    return result['result']
