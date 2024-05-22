from flask import Response

from flask_auditor import AuditLoggerConfig
from flask_auditor import ResponseLogger
from flask_auditor import attributes


def test_extract_response_log():
    cfg = AuditLoggerConfig(
        not_available='not_available',
        log_status_code=True,
        log_status=True,
        log_response_size=True)
    logger = ResponseLogger(cfg)

    flask_resp = Response('hello, world!', status=201)
    log_values = logger.extract(flask_resp)
    assert log_values[attributes.RESPONSE_STATUS_CODE] == 201
    assert log_values[attributes.RESPONSE_STATUS] == 'Created'
    assert log_values[attributes.RESPONSE_SIZE]

    flask_resp = Response(status=204)
    log_values = logger.extract(flask_resp)
    assert log_values[attributes.RESPONSE_SIZE] == cfg.not_available
