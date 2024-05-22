from flask_auditor import attributes

log_values = {}


def test_flask_auditor(extension_factory):
    app, auditor = extension_factory(
        configs={
            'AUDIT_LOGGER_SOURCE_NAME': 'pytest',
            'AUDIT_LOGGER_DATETIME_FORMAT': '%Y-%m-%d',
        })

    def handler(audit_log):
        global log_values
        log_values = audit_log

    def hook(flask_req, flask_resp):
        return {'appId': 'makai', 'actorId': 'kill-vearn'}

    auditor.register_log_handler(handler)
    auditor.register_hook(hook)
    with app.test_client() as client:
        client.post(
            '/api/v1/users',
            json={'name': 'makai', 'password': 'my-password'},
            headers={'User-Agent': 'python/flask-auditor 1.0.0'})
        global log_values
        assert log_values.get(attributes.START_TIME)
        assert log_values.get(attributes.SOURCE_NAME) == 'pytest'
        assert log_values.get(attributes.REQUEST)
        assert log_values.get(attributes.RESPONSE)
        assert log_values.get('actorId') == 'kill-vearn'
        assert log_values.get('appId') == 'makai'
        assert log_values.get(attributes.ACTION_ID) == 'CREATE_USER'
        assert log_values.get(attributes.ACTION_DESCRIPTION) == 'Create user'
        assert 'password' not in log_values[attributes.REQUEST][
            attributes.REQUEST_BODY]
