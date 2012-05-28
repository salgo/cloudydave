from CloudyDave import CloudyDave
from config import notify


cd = CloudyDave()
domain = cd.getDomain()

# We intend to use the notify domain so init that
cd.notifyInit()

for testhost in notify:
    for test in notify[testhost]:
        cd.notifyCheck(testhost, test)
