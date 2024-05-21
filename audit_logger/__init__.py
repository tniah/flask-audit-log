"""An Flask extension to log audit logs."""
import logging
from datetime import datetime
from threading import Thread
from typing import Callable
from typing import Optional

import flask
from flask import Flask
from flask import Response
from flask import request as flask_request

from audit_logger import attributes
from audit_logger.config import AuditLoggerConfig
from audit_logger.request import RequestLogger
from audit_logger.response import ResponseLogger


class FlaskAuditLogger:
    """Flask extension to log audit logs."""

    def __init__(self, app: Optional[Flask] = None) -> None:
        """Initializes an object of the FlaskAuditLog.

        Args:
            app: Instance of the Flask application.
        """
        self._views = {}
        self._hook: Optional[Callable] = None
        self._log_handlers = set()
        self._cfg: Optional[AuditLoggerConfig] = None
        self.app = None
        self.request_logger: Optional[RequestLogger] = None
        self.response_logger: Optional[ResponseLogger] = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Allow to lazy initialize the FlaskAuditLogger object.

        Args:
            app: Instance of the Flask application.
        """
        cfg_options = {}
        for key, value in app.config.items():
            if not key.startswith('AUDIT_LOGGER'):
                continue

            key = key.replace('AUDIT_LOGGER_', '').lower()
            if key in AuditLoggerConfig.options:
                cfg_options[key] = value

        self._cfg = AuditLoggerConfig(**cfg_options)
        if self._cfg.skip is True:
            return None

        self.request_logger = RequestLogger(self._cfg)
        self.response_logger = ResponseLogger(self._cfg)
        self.app = app

        @app.after_request
        def after_request(resp: Response) -> Response:
            endpoint = flask_request.endpoint
            if not endpoint or endpoint not in app.view_functions:
                return resp

            view = app.view_functions[endpoint]
            if hasattr(view, 'view_class'):
                view = view.view_class

            view_location = '.'.join((view.__module__, view.__qualname__))
            method = flask_request.method.lower()
            if f'{view_location}.{method}' in self._views:
                kwargs = self._views.get(f'{view_location}.{method}')
            elif view_location in self._views:
                kwargs = self._views.get(view_location)
            else:
                return resp

            if self._hook:
                extra = self._hook(flask.request, resp)
                if extra and isinstance(extra, dict):
                    kwargs['extra'] = extra

            thr = Thread(
                target=self._extract,
                args=(app, flask.request.environ.copy(), resp),
                kwargs=kwargs)
            thr.start()
            return resp

    def log(self, action_id, description: Optional[str] = None):
        """A decorator to extract audit logs.

        Args:
            action_id: Unique identifier for the action.
            description: A description of the action.
        """

        def wrapper(view):
            view_location = '.'.join((view.__module__, view.__qualname__))
            self._views[view_location] = {
                'action_id': action_id,
                'description': description
            }
            return view

        return wrapper

    def _extract(self, app: Flask, environ,
                 flask_resp: Response, action_id: str,
                 description: str, extra: Optional[dict] = None) -> dict:
        """Extract Flask request and response to audit log.

        Args:
            app: Instance of the Flask application.
            environ: WSGIEnvironment object.
            flask_resp: Flask response object.
            action_id: Unique identifier of the action.
            description: A description of the action.
            extra: Extra information to include in audit log.
        """
        with app.request_context(environ):
            now = datetime.now()
            audit_log = {
                attributes.START_TIME: now.strftime('%Y-%m-%d %H:%M:%S'),
                attributes.ACTION_ID: action_id,
                attributes.ACTION_DESCRIPTION: description,
                attributes.REQUEST: self.request_logger.extract(flask.request),
                attributes.RESPONSE: self.response_logger.extract(flask_resp)
            }
            if self._cfg.log_latency:
                latency = datetime.now().timestamp() - now.timestamp()
                audit_log[attributes.LATENCY] = round(latency, 5)

            if isinstance(extra, dict):
                audit_log.update(extra)

            if not self._log_handlers:
                self.default_log_handler(audit_log)
            else:
                for handler in self._log_handlers:
                    handler(audit_log)
            return audit_log

    @property
    def default_log_handler(self) -> Callable:
        """Default audit log handler."""
        self.app.logger.setLevel(logging.INFO)

        def handler(audit_log: dict):
            self.app.logger.info('FlaskAuditLogger: %s', audit_log)

        return handler

    def register_log_handler(self, handler: Callable) -> None:
        """Register an audit log handler."""
        if not isinstance(handler, Callable):
            raise TypeError("Handler must be callable.")

        self._log_handlers.add(handler)

    def register_hook(self, hook: Callable) -> None:
        """Register a hook to extract more information from request and
        response for audit log."""
        if not isinstance(hook, Callable):
            raise TypeError("Hook must be callable.")

        self._hook = hook
