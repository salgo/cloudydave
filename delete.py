from CloudyDave import CloudyDave

cd = CloudyDave()
domain = cd.getDomain()

#rs = domain.select("SELECT * FROM " + domain.name + " WHERE testhost = 'starbuck.salgo.net' AND timestamp > '0' AND test = 'http' ORDER BY timestamp DESC")
#for item in rs:
#    print item

rs = domain.select("SELECT * FROM " + domain.name)
for item in rs:
    print "deleting", item
    domain.delete_item(item)
