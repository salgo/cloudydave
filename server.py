from flask import Flask
from flask import request
import json

app = Flask(__name__)


@app.route("/report/<host>", methods=['PUT'])
def report(host):

    print json.loads(request.data)

    return 'cheers'

if __name__ == "__main__":
    app.run(debug=True)
