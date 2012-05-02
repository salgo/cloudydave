from CloudyDave import CloudyDave
from config import config
from sys import argv

cd = CloudyDave()
domain = cd.getDomain()

argv.pop(0) # <-- shift

# Fudge together a simple command line query thing.

query = ""

while len(argv) > 2:
    key = argv.pop(0)
    eq = argv.pop(0)
    value = argv.pop(0)
    query += ' AND ' + key + ' ' + eq + " '" + value + "'"

#rs = domain.select("SELECT * FROM " + domain.name + " WHERE testhost = 'starbuck.salgo.net' AND timestamp > '0' AND test = 'http' ORDER BY timestamp DESC")
#for item in rs:
#    print item

#rs = domain.select("SELECT * FROM " + domain.name + " where testhost = 'secure.littoralis.com' and test = 'https'");
rs = domain.select("SELECT * FROM " + domain.name + " WHERE timestamp > '0' " + query + " ORDER BY timestamp DESC")
for item in rs:
    print "--"
    for key in item:
        print key, '=', item[key]