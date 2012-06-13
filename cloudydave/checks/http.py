
from _httpcommon import httpcheck


class HttpCheck(object):

    def test(self, cd, host, params):
        return httpcheck(cd, host, params)
