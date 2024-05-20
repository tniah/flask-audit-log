from typing import Optional

from flask import Flask, request as flask_request

from audit_logger.config import AuditLoggerConfig
from audit_logger.request import RequestLogger


class FlaskAuditLogger:

    def __init__(self, app: Optional[Flask] = None) -> None:
        """Initializes an object of the FlaskAuditLog.

            Args:
                app: Instance of the Flask application.
        """
        self.app = None
        self.request_logger: Optional[RequestLogger] = None
        self.cfg: Optional[AuditLoggerConfig] = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.cfg = AuditLoggerConfig(
            skip=app.config.get('AUDIT_LOGGER_SKIP', False),
            log_remote_ip=app.config.get('AUDIT_LOGGER_REMOTE_IP', True),
            log_remote_port=app.config.get('AUDIT_LOGGER_REMOTE_PORT', True),
            log_request_id=app.config.get('AUDIT_LOGGER_REQUEST_ID', True), )

        if self.cfg.skip is True:
            return None

        self.request_logger = RequestLogger(self.cfg)

        @app.before_request
        def before_request() -> None:
            self.log()

    def log(self):
        import json
        event = self.request_logger.log(flask_request)
        # print(event)
        print(json.dumps(event, indent=2))
