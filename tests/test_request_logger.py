from flask import Flask
from flask_auditor import AuditLoggerConfig
from flask_auditor import RequestLogger
from flask_auditor import attributes


def test_get_request_body():
    app = Flask(__name__)
    expected = {'name': 'makai'}
    logger = RequestLogger()
    with app.test_request_context(json=expected) as ctx:
        assert logger.get_request_body(ctx.request) == expected

    with app.test_request_context(data=expected) as ctx:
        assert logger.get_request_body(ctx.request) == expected

    with app.test_request_context(data=expected, mimetype='text/plain') as ctx:
        assert logger.get_request_body(ctx.request) == {}


def test_extract_request_log():
    app = Flask(__name__)
    cfg = AuditLoggerConfig(
        not_available='NA',
        log_server=True,
        log_request_id=True,
        log_remote_ip=True,
        log_remote_port=True,
        log_protocol=True,
        log_host=True,
        log_method=True,
        log_uri=True,
        log_uri_path=True,
        log_route_path=True,
        log_referer=True,
        log_user_agent=True,
        log_content_length=True,
        log_request_headers=True,
        log_query_params=True,
        log_request_body=True)
    logger = RequestLogger(cfg)
    with app.test_request_context(
            '/api/v1/users',
            method='POST',
            query_string='client_id=makai',
            json={'name': 'makai'},
            headers=[
                ('Content-Type', 'application/json'),
                ('X-Request-Id', 'test-request-id'),
                ('Referer', 'https://example.com:8080'),
                ('User-Agent', 'python/flask-auditor 1.0'),
                ('X-Forwarded-For', '10.10.10.100'),
                ('X-Real-Ip', '192.168.1.10'),
            ],
            base_url='https://example.com:8080',
            environ_overrides={
                'REMOTE_PORT': 28969
            }) as ctx:
        log_values = logger.extract(ctx.request)
        assert log_values[attributes.SERVER_HOST] == 'example.com'
        assert log_values[attributes.SERVER_PORT] == 8080
        assert log_values[attributes.REQUEST_ID] == 'test-request-id'
        assert log_values[attributes.REQUEST_REMOTE_IP] == '192.168.1.10'
        assert log_values[attributes.REQUEST_REMOTE_PORT] == 28969
        assert log_values[attributes.REQUEST_PROTOCOL] == 'HTTP/1.1'
        assert log_values[attributes.REQUEST_HOST] == 'example.com:8080'
        assert log_values[attributes.REQUEST_METHOD] == 'POST'
        assert (log_values[attributes.REQUEST_URI]
                == '/api/v1/users?client_id=makai')
        assert log_values[attributes.REQUEST_ROUTE_PATH] == cfg.not_available
        assert (log_values[attributes.REQUEST_HTTP_REFERER]
                == 'https://example.com:8080')
        assert (log_values[attributes.REQUEST_USER_AGENT]
                == 'python/flask-auditor 1.0')
        assert log_values[attributes.REQUEST_CONTENT_LENGTH]
        assert log_values[attributes.REQUEST_HEADERS] == {
            'X-Forwarded-For': '10.10.10.100',
            'Content-Type': 'application/json'
        }
        assert (log_values[attributes.REQUEST_QUERY_PARAMS]
                == {'client_id': ['makai']})
        assert log_values[attributes.REQUEST_BODY] == {'name': 'makai'}
