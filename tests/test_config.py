import pytest
from flask_auditor import AuditLoggerConfig


@pytest.mark.parametrize('options', [{
    'not_available': 'notAvailable',
    'source_name': 'testSourceName',
    'datetime_format': '%Y%m%d%H%M%S',
    'skip': not AuditLoggerConfig.skip,
    'log_server': not AuditLoggerConfig.log_server,
    'log_latency': not AuditLoggerConfig.log_latency,
    'log_protocol': not AuditLoggerConfig.log_protocol,
    'log_remote_ip': not AuditLoggerConfig.log_remote_ip,
    'log_remote_port': not AuditLoggerConfig.log_remote_port,
    'log_host': not AuditLoggerConfig.log_host,
    'log_method': not AuditLoggerConfig.log_method,
    'log_uri': not AuditLoggerConfig.log_uri,
    'log_uri_path': not AuditLoggerConfig.log_uri_path,
    'log_route_path': not AuditLoggerConfig.log_route_path,
    'log_request_id': not AuditLoggerConfig.log_request_id,
    'log_referer': not AuditLoggerConfig.log_referer,
    'log_user_agent': not AuditLoggerConfig.log_user_agent,
    'log_status_code': not AuditLoggerConfig.log_status_code,
    'log_status': not AuditLoggerConfig.log_status,
    'log_content_length': not AuditLoggerConfig.log_content_length,
    'log_response_size': not AuditLoggerConfig.log_response_size,
    'log_request_headers': not AuditLoggerConfig.log_request_headers,
    'log_query_params': not AuditLoggerConfig.log_query_params,
    'log_request_body': not AuditLoggerConfig.log_request_body,
    'log_sensitive_data': not AuditLoggerConfig.log_sensitive_data,
    'default_request_headers': ('X-Request-Header', 'X-Request-Header-Value'),
    'default_sensitive_parameters': ('X-Sensitive-Data',)
}])
def test_audit_logger_config(options):
    cfg = AuditLoggerConfig(**options)
    for opt in options:
        assert getattr(cfg, opt) == options[opt]
