from CloudyDave import CloudyDave
from sys import argv
from datetime import datetime

cd = CloudyDave()
domain = cd.getDomain()

# Fudge together a simple command line query thing.

query, limit = cd.commandArgs(argv)
query = "SELECT * FROM " + domain.name + " WHERE " + query + " ORDER BY timestamp DESC"
rs = domain.select(query)

for item in rs:
    dt = datetime.fromtimestamp(int(item['timestamp']))
    date = dt.isoformat()

    print "{},{}".format(date, item['value'])
