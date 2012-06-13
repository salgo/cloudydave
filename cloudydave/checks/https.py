
from _httpcommon import httpcheck


class HttpsCheck(object):

    def test(self, cd, host, params):
        return httpcheck(cd, host, params, True)
