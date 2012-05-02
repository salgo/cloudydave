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
    
    if key == 'limit': 
        limit = int(eq)
        continue 
        
    value = argv.pop(0)
    query += ' AND ' + key + ' ' + eq + " '" + value + "'"

query = "SELECT * FROM " + domain.name + " WHERE timestamp > '0' " + query + " ORDER BY timestamp DESC"

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