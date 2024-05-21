"""Implements the Response Logger."""
from flask import Response
from werkzeug import http

from audit_logger import attributes
from audit_logger.base import BaseAuditLogger


class ResponseLogger(BaseAuditLogger):
    """Response logger class to extract http response parameters."""

    def extract(self, flask_resp: Response) -> dict:
        """Extract response audit log."""
        log_values = {}

        if self.cfg.log_status_code:
            log_values[attributes.RESPONSE_STATUS_CODE] = self.get_status_code(
                flask_resp)

        if self.cfg.log_status:
            log_values[attributes.RESPONSE_STATUS] = self.get_status(flask_resp)

        if self.cfg.log_response_size:
            log_values[attributes.RESPONSE_SIZE] = self.get_response_size(
                flask_resp)

        return log_values

    @staticmethod
    def get_status_code(flask_resp: Response) -> int:
        """Return HTTP status code.

        Args:
            flask_resp: Flask response object.
        """
        return flask_resp.status_code

    @staticmethod
    def get_status(flask_resp: Response) -> str:
        """Return HTTP status code as a string.

        Args:
            flask_resp: Flask response object.
        """
        return http.HTTP_STATUS_CODES[flask_resp.status_code]

    @staticmethod
    def get_response_size(flask_resp: Response) -> int:
        """Return the `Content-Length` header value as an int.

        Args:
            flask_resp: Flask response object.
        """
        return flask_resp.content_length
