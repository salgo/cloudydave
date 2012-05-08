from CloudyDave import CloudyDave
from config import notify
from twilio.rest import TwilioRestClient
from config import Twilio_AccountSID
from config import Twilio_AuthToken
from config import Twilio_SenderNumber

cd = CloudyDave()
domain = cd.getDomain()

for testhost in notify:
    for test in notify[testhost]:
        query = "SELECT * FROM {} WHERE timestamp > '0' AND testhost = '{}' AND test = '{}' AND key = '{}' ORDER BY timestamp DESC".format(domain.name, testhost, test['test'], test['key'], test['value'])
        rs = domain.select(query, max_items=1)

        for item in rs:
            if item['value'] == test['value']:
                client = TwilioRestClient(Twilio_AccountSID, Twilio_AuthToken)

                message = client.sms.messages.create(to=test['notify-number'],
                                                     from_=Twilio_SenderNumber,
                                                     body=testhost + ' ' + item['test'] + ' ' + unicode(item['value']))
