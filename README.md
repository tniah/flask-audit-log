# Flask-Audit-Log

Flask-Audit-Log is an extension for Flask that extract request and response to audit log.

## Installing
Install and upgrade using pip:
```shell
$ pip install flask-audit-log
```

##  A simple example
```py
from flask import Flask
from flask import jsonify
from flask import request
from flask.views import MethodView

from audit_logger import FlaskAuditLogger

app = Flask(__name__)
app.config['AUDIT_LOGGER_SKIP'] = False
app.config['AUDIT_LOGGER_SOURCE_NAME'] = 'classBasedViewExample'
audit = FlaskAuditLogger(app)


@audit.log(action_id='GET_USER', description='Fetch a single user by ID')
class UserView(MethodView):

    def get(self, user_id):
        """Handles GET requests."""
        resp = jsonify({
            'id': user_id,
            'name': 'Makai'
        })
        resp.status_code = 200
        return resp


class UsersView(MethodView):

    @audit.log(action_id='GET_USERS', description='Fetch all users')
    def get(self):
        """Handles GET requests."""
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

    @audit.log(action_id='CREATE_USER', description='Create a new user')
    def post(self):
        """Handles POST requests."""
        if request.is_json:
            name = request.json.get('name')
            if not name:
                resp = jsonify({
                    'error': 'validation_failed',
                    'error_description': 'Please provide a name.'
                })
                resp.status_code = 400
                return resp

            return jsonify({
                'id': 1,
                'name': name
            })

        resp = jsonify({
            'error': 'unsupported_media_type',
            'error_description': 'Media type is not supported.'
        })
        resp.status_code = 415
        return resp


app.add_url_rule('/api/v1/users', view_func=UsersView.as_view('users'))
app.add_url_rule('/api/v1/users/<int:user_id>',
                 view_func=UserView.as_view('user'))

if __name__ == '__main__':
    app.run(debug=True)

```