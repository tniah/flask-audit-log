"""Implements the Request Logger."""
from flask import Request
from audit_logger import attributes
from urllib.parse import parse_qs
from audit_logger import AuditLoggerConfig
from typing import Optional


class RequestLogger:
    """Request logger class to extract Http request parameters."""

    def __init__(self, cfg: Optional[AuditLoggerConfig] = None):
        """Initialize an object of the RequestLogger class.

        Args:
            cfg (Optional[AuditLoggerConfig]): Configuration object.
        """
        if cfg is None:
            cfg = AuditLoggerConfig()

        self.cfg = cfg

    def log(self, flask_req: Request) -> dict:
        """Extract request audit log.

        Args:
            flask_req (Request): Flask request object.

        Return:
             A dictionary.
        """
        log_values = {}

        if self.cfg.log_server:
            host, port = self.get_server_info(flask_req)
            log_values[attributes.SERVER_HOST] = host
            log_values[attributes.SERVER_PORT] = port

        if self.cfg.log_request_id:
            log_values[attributes.REQUEST_ID] = self.get_request_id(flask_req)

        if self.cfg.log_remote_ip:
            log_values[attributes.REQUEST_REMOTE_IP] = self.get_remote_address(
                flask_req)

        if self.cfg.log_remote_port:
            log_values[attributes.REQUEST_REMOTE_PORT] = self.get_remote_port(
                flask_req)

        if self.cfg.log_protocol:
            log_values[attributes.REQUEST_PROTOCOL] = self.get_protocol(
                flask_req)

        if self.cfg.log_host:
            log_values[attributes.REQUEST_HOST] = self.get_host(flask_req)

        if self.cfg.log_method:
            log_values[attributes.REQUEST_METHOD] = self.get_method(flask_req)

        if self.cfg.log_uri:
            log_values[attributes.REQUEST_URI] = self.get_uri(flask_req)

        if self.cfg.log_uri_path:
            log_values[attributes.REQUEST_URI_PATH] = self.get_uri_path(
                flask_req)

        if self.cfg.log_route_path:
            log_values[attributes.REQUEST_ROUTE_PATH] = self.get_route_path(
                flask_req)

        if self.cfg.log_referer:
            log_values[attributes.REQUEST_HTTP_REFERER] = self.get_http_referer(
                flask_req)

        if self.cfg.log_user_agent:
            log_values[attributes.REQUEST_USER_AGENT] = self.get_user_agent(
                flask_req)

        if self.cfg.log_content_length:
            key = attributes.REQUEST_CONTENT_LENGTH
            log_values[key] = self.get_content_length(flask_req)

        if self.cfg.log_request_headers:
            log_values[attributes.REQUEST_HEADERS] = self.get_headers(flask_req)

        if self.cfg.log_query_params:
            log_values[attributes.REQUEST_QUERY_PARAMS] = self.get_query_params(
                flask_req)

        if self.cfg.log_request_body:
            req_body = self.get_request_body(flask_req)
            if not self.cfg.log_sensitive_data:
                req_body = self.remove_sensitive_parameters(req_body)

            log_values[attributes.REQUEST_BODY] = req_body

        return log_values

    @staticmethod
    def get_server_info(flask_req: Request):
        """Return address (host, port) of server.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.server

    @staticmethod
    def get_request_id(flask_req: Request):
        """Return request id from request `X-Request-Id` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('HTTP_X_REQUEST_ID')

    @staticmethod
    def get_remote_address(flask_req: Request):
        """Return the real IP of the client sending the request.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('HTT_X_REAL_IP', flask_req.remote_addr)

    @staticmethod
    def get_remote_port(flask_req: Request):
        """Return the remote port of the client sending the request.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('REMOTE_PORT')

    @staticmethod
    def get_protocol(flask_req: Request):
        """Return http version used by server.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('SERVER_PROTOCOL')

    @staticmethod
    def get_host(flask_req: Request):
        """Return host name from request `Host` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.host

    @staticmethod
    def get_method(flask_req: Request):
        """Return the method the request was made with.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.method

    @staticmethod
    def get_uri(flask_req: Request):
        """Return requested path, including the query string.

        Args:
            flask_req (Request): Flask request object.
        """
        uri = flask_req.full_path
        if uri and uri.endswith('?'):
            return uri[:-1]
        else:
            return uri

    @staticmethod
    def get_uri_path(flask_req: Request):
        """Return requested path, excluding the query string.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.path

    @staticmethod
    def get_route_path(flask_req: Request):
        """Path pattern which request was matched.

        Args:
            flask_req (Request): Flask request object.
        """
        if flask_req.url_rule:
            return flask_req.url_rule.rule

    @staticmethod
    def get_http_referer(flask_req: Request):
        """Return http referer from request `Referer` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.referrer

    @staticmethod
    def get_user_agent(flask_req: Request):
        """Return user agent from request `User-Agent` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.user_agent.to_header()

    @staticmethod
    def get_content_length(flask_req: Request):
        """Return the ``Content-Length`` header value as an int.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.content_length

    def get_headers(self, flask_req: Request, headers: Optional[tuple] = None):
        """Return headers received with the request.

        Args:
            flask_req (Request): Flask request object.
            headers (Optional[tuple]): A list of headers to extract.
        """

        if headers is None:
            headers = self.cfg.default_request_headers

        return {
            key: flask_req.headers.get(key)
            for key in headers if key in flask_req.headers
        }

    @staticmethod
    def get_query_params(flask_req: Request):
        """Return request query string. The part of the URL after the `?`.

        Args:
            flask_req (Request): Flask request object.
        """
        return parse_qs(flask_req.query_string.decode('UTF-8'))

    @staticmethod
    def get_request_body(flask_req: Request):
        """Return request body.

        Args:
            flask_req (Request): Flask request object.
        """
        if flask_req.is_json:
            return flask_req.get_json()
        elif flask_req.form:
            return flask_req.form
        else:
            return flask_req.data.decode('UTF-8')

    def remove_sensitive_parameters(
            self, params: dict,
            sensitive_params: Optional[tuple] = None) -> dict:
        """Remove sensitive data i.e, `password`, `secret_key`.

        Args:
            params: A dictionary of parameters maybe contain sensitive data
            sensitive_params: A list of sensitive parameters must be removed
                              from the given dict.
        """
        if not isinstance(params, dict):
            return params

        if sensitive_params is None:
            sensitive_params = self.cfg.default_sensitive_parameters

        return {k: v for k, v in params.items() if k not in sensitive_params}
