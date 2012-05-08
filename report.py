from CloudyDave import CloudyDave
from sys import argv

cd = CloudyDave()
domain = cd.getDomain()

query, limit = cd.commandArgs(argv)
query = "SELECT * FROM " + domain.name + " WHERE " + query

rs = domain.select(query)

uniques = {}
unique_fields = ['fromhost', 'testhost', 'test', ('test', 'key')]

for item in rs:

    for field in unique_fields:
        if isinstance(field, tuple):
            key = field[0] + '/' + field[1]
        else:
            key = field

        if not(key in uniques):
            uniques[key] = []

        if isinstance(field, tuple):

            value = item[field[0]] + '/' + item[field[1]]
        else:
            value = item[field]

        if not(value in uniques[key]):
            uniques[key].append(value)

for u in uniques:
    print u
    for item in uniques[u]:
        print "\t", item
