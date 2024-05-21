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
from flask.views import MethodView
from flask_auditor import FlaskAuditor

app = Flask(__name__)
app.config['AUDIT_LOGGER_SKIP'] = False
app.config['AUDIT_LOGGER_SOURCE_NAME'] = 'classBasedViewExample'
audit = FlaskAuditor(app)


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


app.add_url_rule('/api/v1/users', view_func=UsersView.as_view('users'))
app.add_url_rule('/api/v1/users/<int:user_id>',
                 view_func=UserView.as_view('user'))

if __name__ == '__main__':
    app.run(debug=True)
```