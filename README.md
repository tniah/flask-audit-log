# Flask-Auditor

Flask-Auditor is an extension for Flask that extract request and response to audit log.

## Installing

Install and upgrade using pip:

```shell
$ pip install flask_auditor
```

## A simple example

```py
from flask import Flask
from flask import jsonify

from flask_auditor import FlaskAuditor

app = Flask(__name__)
app.config['AUDIT_LOGGER_SOURCE_NAME'] = 'auditLogger'
auditor = FlaskAuditor(app)


@app.route('/api/v1/users', methods=['GET'])
@auditor.log(action_id='LIST_USERS', description='Fetch a list of users')
def list_users():
    resp = jsonify({
        'users': [
            {
                'id': 1,
                'name': 'Makai'
            },
            {
                'id': 2,
                'name': 'TNiaH'
            }
        ]
    })
    resp.status_code = 200
    return resp


if __name__ == '__main__':
    app.run(debug=True)

```

## Audit Log Example

```json
{
  "source": "auditLogger",
  "startTime": "2024-05-22 11:45:42",
  "actionId": "LIST_USERS",
  "description": "Fetch a list of users",
  "request": {
    "serverHost": "127.0.0.1",
    "serverPort": 5000,
    "requestID": "N/A",
    "remoteIP": "127.0.0.1",
    "remotePort": 34038,
    "protocol": "HTTP/1.1",
    "host": "127.0.0.1:5000",
    "method": "GET",
    "uri": "/api/v1/users?page=1&limit=10",
    "uriPath": "/api/v1/users",
    "routePath": "/api/v1/users",
    "referer": "N/A",
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "contentLength": "N/A",
    "headers": {
      "Accept-Encoding": "gzip, deflate, br"
    },
    "queryParams": {
      "page": [
        "1"
      ],
      "limit": [
        "10"
      ]
    },
    "requestBody": {}
  },
  "response": {
    "statusCode": 200,
    "status": "OK",
    "responseSize": 120
  },
  "latency": 0.00011
}
```