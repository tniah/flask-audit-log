"""Implements the Request Logger."""
from typing import Optional
from typing import Tuple
from urllib.parse import parse_qs

from flask import Request

from audit_logger import attributes
from audit_logger.base import BaseAuditLogger


class RequestLogger(BaseAuditLogger):
    """Request logger class to extract Http request parameters."""

    def extract(self, flask_req: Request) -> dict:
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

        return self.convert_none_record(log_values)

    @staticmethod
    def get_server_info(flask_req: Request) -> Tuple[str, int]:
        """Return address (host, port) of server.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.server

    @staticmethod
    def get_request_id(flask_req: Request) -> str:
        """Return request id from request `X-Request-Id` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('HTTP_X_REQUEST_ID')

    @staticmethod
    def get_remote_address(flask_req: Request) -> str:
        """Return the real IP of the client sending the request.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('HTT_X_REAL_IP', flask_req.remote_addr)

    @staticmethod
    def get_remote_port(flask_req: Request) -> str:
        """Return the remote port of the client sending the request.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('REMOTE_PORT')

    @staticmethod
    def get_protocol(flask_req: Request) -> str:
        """Return http version used by server.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.environ.get('SERVER_PROTOCOL')

    @staticmethod
    def get_host(flask_req: Request) -> str:
        """Return host name from request `Host` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.host

    @staticmethod
    def get_method(flask_req: Request) -> str:
        """Return the method the request was made with.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.method

    @staticmethod
    def get_uri(flask_req: Request) -> str:
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
    def get_uri_path(flask_req: Request) -> str:
        """Return requested path, excluding the query string.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.path

    @staticmethod
    def get_route_path(flask_req: Request) -> str:
        """Path pattern which request was matched.

        Args:
            flask_req (Request): Flask request object.
        """
        if flask_req.url_rule:
            return flask_req.url_rule.rule

    @staticmethod
    def get_http_referer(flask_req: Request) -> str:
        """Return http referer from request `Referer` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.referrer

    @staticmethod
    def get_user_agent(flask_req: Request) -> str:
        """Return user agent from request `User-Agent` header.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.user_agent.to_header()

    @staticmethod
    def get_content_length(flask_req: Request) -> int | None:
        """Return the ``Content-Length`` header value as an int.

        Args:
            flask_req (Request): Flask request object.
        """
        return flask_req.content_length

    def get_headers(self, flask_req: Request,
                    headers: Optional[tuple] = None) -> dict:
        """Return headers received with the request.

        Args:
            flask_req (Request): Flask request object.
            headers (Optional[tuple]): A list of headers to retrieve.
        """

        if headers is None:
            headers = self.cfg.default_request_headers

        return {
            key: flask_req.headers.get(key)
            for key in headers if key in flask_req.headers
        }

    @staticmethod
    def get_query_params(flask_req: Request) -> dict:
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
        mt = flask_req.mimetype
        if (mt == "application/json" or mt.startswith("application/")
                and mt.endswith("+json")):
            return flask_req.get_json()
        elif (mt == "multipart/form-data"
              or mt == "application/x-www-form-urlencoded"):
            return flask_req.form
        else:
            # do not extract other mimetypes
            return {}
