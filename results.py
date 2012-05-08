from CloudyDave import CloudyDave
from sys import argv
from datetime import datetime

cd = CloudyDave()
domain = cd.getDomain()

# Fudge together a simple command line query thing.

query, limit = cd.commandArgs(argv)
query = "SELECT * FROM " + domain.name + " WHERE " + query + " ORDER BY timestamp DESC"

print query, "\n"

rs = domain.select(query, max_items=limit)
c = 0
for item in rs:
    print "--"
    c += 1
    for key in item:
        if key == 'timestamp':
            dt = datetime.fromtimestamp(int(item[key]))
            print key, '=', dt.isoformat()
        else:
            print key, '=', item[key]

print "\n", c, "items returned\n"
