from CloudyDave import CloudyDave
from config import config
from sys import argv
from datetime import datetime

cd = CloudyDave()
domain = cd.getDomain()

argv.pop(0) # <-- shift off cmd name

# Fudge together a simple command line query thing.

query = ""
limit = None

while len(argv) > 1:
    key = argv.pop(0)
    eq = argv.pop(0)
    value = argv.pop(0)
    query += ' AND ' + key + ' ' + eq + " '" + value + "'"

query = "SELECT * FROM " + domain.name + " WHERE timestamp > '0' " + query + " ORDER BY timestamp DESC"
rs = domain.select(query)

for item in rs:
    dt = datetime.fromtimestamp(int(item['timestamp']))
    date = dt.isoformat()
    
    print "{},{}".format(date, item['value'])