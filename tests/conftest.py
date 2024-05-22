import pytest
from flask import Flask
from flask import jsonify
from flask import request
from flask_auditor import FlaskAuditor


@pytest.fixture(scope='session')
def extension_factory():
    def factory(configs=None):
        app = Flask(__name__)
        if configs is None:
            configs = {}

        app.config.update(configs)
        auditor = FlaskAuditor(app)

        @app.route('/api/v1/users', methods=['POST'])
        @auditor.log(action_id='CREATE_USER', description='Create user')
        def create_user():
            if not request.is_json:
                resp = jsonify({'error': 'unsupported_media_type'})
                resp.status_code = 415
                return resp

            data = request.get_json()
            if 'name' not in data:
                resp = jsonify({'error': '"name" is required'})
                resp.status_code = 400
                return resp

            name = data['name']
            resp = jsonify({'name': name, 'id': 1})
            resp.status_code = 201
            return resp

        @app.route('/api/v1/users/<int:user_id>', methods=['GET'])
        @auditor.log(action_id='GET_USER', description='Get user')
        def get_user(user_id):
            resp = jsonify({'id': user_id, 'name': 'Makai'})
            resp.status_code = 200
            return resp

        return app, auditor

    return factory
