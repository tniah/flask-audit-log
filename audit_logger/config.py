from typing import Optional


class AuditLoggerConfig:
    # Set to true to disable audit logger
    skip = False

    # Instructs logger to record server information
    log_server = True

    # Instructs logger to record duration it took to extract and save log.
    log_latency = True

    # Instructs logger to extract request protocol (i.e. `HTTP/1.1` or `HTTP/2`)
    log_protocol = True

    # Instructs logger to extract request remote IP.
    log_remote_ip = True

    # Instructs logger to extract request remote port
    log_remote_port = True

    # Instructs logger to extract request host value (i.e, `example.com`)
    log_host = True

    # Instructs logger to extract request method value (i.e, `POST`)
    log_method = True

    # Instruct logger to extract request URI (i.e, `/api/v1/users?lange=vi`)
    log_uri = True

    # Instruct logger to extract request URI path (i.e, `/api/v1/users`)
    log_uri_path = True

    # Instruct logger to extract route path part to which request was matched
    # (i.e, `/api/v1/users/<string:user_id>`)
    log_route_path = True

    # Instructs logger to extract request ID from request `X-Request-Id` header
    # or response if request did not have value
    log_request_id = True

    # Instructs logger to extract request referer values
    log_referer = True

    # Instructs logger to extract request user agent values
    log_user_agent = True

    # Instructs logger to extract response status code.
    log_status = True

    # Instructs logger to extract error returned from executed handlers.
    log_error = True

    # Instructs logger to extract content length header value.
    log_content_length = True

    # Instructs logger to extract response content length value.
    log_response_size = True

    # Instructs logger to extract response body.
    log_response_body = True

    # Instructs logger to extract given list of headers from request.
    log_request_headers = True

    # Instruct logger to extract query parameters from request URI.
    log_query_params = True

    # Instructs logger to extract request body.
    log_request_body = True

    # Instructs logger to extract including sensitive data
    log_sensitive_data = False

    # A default list of headers to instruct logger to extract from request
    default_request_headers = (
        'X-Forwarded-For',
        'Accept-Encoding',
        'Content-Type')

    # A default list of sensitive parameters which logger must not extract
    default_sensitive_parameters = (
        'password',
        'pwd',
        'secret_key',
        'secretKey',
        'private_key',
        'privateKey')

    def __init__(self, **kwargs):
        """Initialize an object of the AuditLogConfig class."""
        keys = (
            'skip',
            'log_latency',
            'log_protocol',
            'log_remote_ip',
            'log_remote_port',
            'log_host',
            'log_method',
            'log_uri',
            'log_uri_path',
            'log_route_path',
            'log_request_id',
            'log_referer',
            'log_user_agent',
            'log_status',
            'log_error',
            'log_content_length',
            'log_response_size',
            'log_request_headers',
            'log_request_body',
            'log_sensitive_data',
            'log_response_body',
        )
        for key in keys:
            if key in kwargs and kwargs[key] is not None:
                setattr(self, key, kwargs[key])
