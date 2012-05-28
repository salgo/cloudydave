from datetime import datetime
from datetime import timedelta

from flask import Flask
from flask import render_template
from flask import request


from CloudyDave import CloudyDave

app = Flask(__name__)


def parse_form_date(datestr, timestr):
    return datetime.strptime(datestr + ' ' + timestr, "%m/%d/%Y %H:%M")


@app.route("/")
def index():

    cd = CloudyDave()
    uniques = cd.reportAgo()

    return render_template('index.html', nodes=uniques['testhost'])


@app.route("/graphs/<testhost>", methods=['GET', 'POST'])
def graphs(testhost):

    cd = CloudyDave()

    uniques = cd.reportAgo()

    fields = ['testhost', 'test/key', 'startdate',
              'starttime', 'enddate', 'endtime']
    query_fields = ['fromhost', 'testhost', 'test/key']
    params = {}
    query = {}
    data = None

    if request.method == 'POST':
        for key in fields:
            if request.form[key] != '':
                params[key] = request.form[key]
                if key in query_fields:
                    query[key] = request.form[key]

        if 'test/key' in query:
            test, key = query['test/key'].split('/')
            query['key'] = key
            query['test'] = test
            del query['test/key']

        if 'startdate' in params and 'starttime' in params:
            startdt = parse_form_date(params['startdate'], params['starttime'])

        if 'enddate' in params and 'endtime' in params:
            enddt = parse_form_date(params['enddate'], params['endtime'])

        data = cd.graphQuery(startdt, enddt, **query)

    else:
        enddt = datetime.utcnow()
        startdt = enddt - timedelta(minutes=60)

        params['startdate'] = startdt.strftime("%m/%d/%Y")
        params['starttime'] = startdt.strftime("%H:%M")
        params['enddate'] = enddt.strftime("%m/%d/%Y")
        params['endtime'] = enddt.strftime("%H:%M")

    return render_template('graphs.html', testkeys=uniques['test/key'],
                           params=params, data=data, testhost=testhost)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
