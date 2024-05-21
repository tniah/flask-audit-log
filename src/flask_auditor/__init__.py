"""A Flask extension to extract audit logs."""
import logging
from datetime import datetime
from threading import Thread
from typing import Callable
from typing import Optional

import flask

from . import attributes
from .config import AuditLoggerConfig
from .request import RequestLogger
from .response import ResponseLogger


class FlaskAuditor:
    """Flask extension to extract audit logs."""

    def __init__(self, app: Optional[flask.Flask] = None) -> None:
        """Initializes an object of the FlaskAuditLog.

        Args:
            app: Instance of the Flask application.
        """
        self._views = {}
        self._hook: Optional[Callable] = None
        self._log_handlers = set()
        self._cfg: Optional[AuditLoggerConfig] = None
        self.app: Optional[flask.Flask] = None
        self.request_logger: Optional[RequestLogger] = None
        self.response_logger: Optional[ResponseLogger] = None
        if app:
            self.init_app(app)

    def init_app(self, app: flask.Flask) -> None:
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
        def after_request(resp: flask.Response) -> flask.Response:
            endpoint = flask.request.endpoint
            if not endpoint or endpoint not in app.view_functions:
                return resp

            view = app.view_functions[endpoint]
            if hasattr(view, 'view_class'):
                view = view.view_class

            view_location = '.'.join((view.__module__, view.__qualname__))
            method = flask.request.method.lower()
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
                args=(self._clone_current_request(), resp),
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

    def _extract(self, flask_req: flask.Request,
                 flask_resp: flask.Response, action_id: str,
                 description: str, extra: Optional[dict] = None) -> dict:
        """Extract Flask request and response to audit log.

        Args:
            flask_req: Flask request object.
            flask_resp: Flask response object.
            action_id: Unique identifier of the action.
            description: A description of the action.
            extra: Extra information to include in audit log.
        """
        now = datetime.now()
        audit_log = {
            attributes.SOURCE_NAME: self._cfg.source_name,
            attributes.START_TIME: now.strftime(self._cfg.datetime_format),
            attributes.ACTION_ID: action_id,
            attributes.ACTION_DESCRIPTION: description,
            attributes.REQUEST: self.request_logger.extract(flask_req),
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

    @staticmethod
    def _clone_current_request() -> flask.Request:
        """Copy current request to Flask request object."""
        flask_req = flask.Request(environ=flask.request.environ.copy())
        flask_req._cached_data = flask.request.get_data()
        flask_req.url_rule = flask.request.url_rule
        return flask_req

    @property
    def default_log_handler(self) -> Callable:
        """Default audit log handler."""
        if self.app.logger.level > logging.INFO:
            self.app.logger.setLevel(logging.INFO)

        def handler(audit_log: dict):
            self.app.logger.info(
                'flask_auditor.FlaskAuditLogger: %s', audit_log)

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
