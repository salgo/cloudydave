from CloudyDave import CloudyDave
from config import config

cd = CloudyDave()
domain = cd.getDomain()

#rs = domain.select("SELECT * FROM " + domain.name + " WHERE testhost = 'starbuck.salgo.net' AND timestamp > '0' AND test = 'http' ORDER BY timestamp DESC")
#for item in rs:
#    print item

#rs = domain.select("SELECT * FROM " + domain.name + " where testhost = 'secure.littoralis.com' and test = 'https'");
rs = domain.select("SELECT * FROM " + domain.name + " WHERE timestamp > '0' AND fromhost = 'bubbles.local' AND test = 'mysql-status' AND key = 'Connections' ORDER BY timestamp DESC")
for item in rs:
    print "--"
    for key in item:
        print key, '=', item[key]