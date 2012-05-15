from twilio.rest import TwilioRestClient

from CloudyDave import CloudyDave

from config import notify
from config import Twilio_AccountSID
from config import Twilio_AuthToken
from config import Twilio_SendNumber

# Useful when one is testing :)
DO_NOT_SEND_TEXTS = False

cd = CloudyDave()
domain = cd.getDomain()

# We intend to use the notify domain so init that
cd.notifyInit()

for testhost in notify:
    for test in notify[testhost]:

        query = "SELECT * FROM {} WHERE timestamp > '0' AND ".format(domain.name)

        if 'testhost' in test:
            # As test host is specified the host specified in the notify is actually the fromhost
            query += " fromhost = '{}' AND testhost = '{}'".format(testhost, test['testhost'])
        else:
            query += "testhost = '{}'".format(testhost)

        query += " AND test = '{}' AND key = '{}' ORDER BY timestamp DESC".format(test['test'], test['key'])

        rs = domain.select(query, max_items=1)

        failed = False
        for item in rs:
            if not('cmp' in test) or test['cmp'] == '=':
                if item['value'] == test['value']:
                    failed = True
            else:
                # number compares
                test_value = float(test['value'])
                actual_value = float(item['value'])

                if test['cmp'] == '>':
                    if actual_value > test_value:
                        failed = True
                elif test['cmp'] == '>=':
                    if actual_value >= test_value:
                        failed = True
                elif test['cmp'] == '<':
                    if actual_value < test_value:
                        failed = True
                elif test['cmp'] == '<=':
                    if actual_value <= test_value:
                        failed = True

        send_notify = cd.notifyStatus(testhost, test, failed)

        if send_notify:

            if failed:
                if 'message' in test:
                    msg = test['message']
                else:
                    msg = 'failed'
            else:
                msg = 'recovered'

            if 'service' in test:
                service = test['service']
            else:
                service = item['test']

            body = "{} on {}: {}".format(service, testhost, msg)

            if not(DO_NOT_SEND_TEXTS):
                client = TwilioRestClient(Twilio_AccountSID, Twilio_AuthToken)
                message = client.sms.messages.create(to=test['notify-number'],
                                                     from_=Twilio_SendNumber,
                                                     body=body)
            else:
                print Twilio_SendNumber, body
