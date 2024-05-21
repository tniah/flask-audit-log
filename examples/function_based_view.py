from flask import Flask
from flask import jsonify
from flask import request

from flask_auditor import FlaskAuditor

app = Flask(__name__)
audit = FlaskAuditor(app)


@app.route('/api/v1/users', methods=['GET'])
@audit.log(action_id='LIST_USERS', description='Fetch a list of users')
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


@app.route('/api/v1/users', methods=['POST'])
@audit.log(action_id='CREATE_USER', description='Create a new user')
def create_user():
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


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@audit.log(action_id='GET_USER', description='Fetch a single user by ID')
def get_user(user_id: int):
    resp = jsonify({
        'id': user_id,
        'name': 'Makai'
    })
    resp.status_code = 200
    return resp


if __name__ == '__main__':
    app.run(debug=True)
