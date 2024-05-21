"""Implement a base class for audit loggers."""
import abc
from typing import Any
from typing import Optional

from .config import AuditLoggerConfig


class BaseAuditLogger(metaclass=abc.ABCMeta):
    """Base class for audit loggers."""

    def __init__(self, cfg: Optional[AuditLoggerConfig] = None):
        """Initialize an object of the class.

        Args:
            cfg (Optional[AuditLoggerConfig]): Configuration object.
        """
        if cfg is None:
            cfg = AuditLoggerConfig()

        self.cfg = cfg

    @abc.abstractmethod
    def extract(self, **kwargs) -> dict:
        """Extract audit logs."""
        raise NotImplementedError("must be implemented in subclass.")

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

    def convert_none_record(
            self, params: dict,
            not_available: Optional[Any] = None) -> dict:
        """Convert none record value to the given value."""
        if not_available is None:
            not_available = self.cfg.not_available

        keys = params.keys()
        for k in keys:
            if params[k] is None:
                params[k] = not_available
            elif isinstance(params[k], dict):
                params[k] = self.convert_none_record(params[k], not_available)
            elif isinstance(params[k], list) or isinstance(params[k], tuple):
                params[k] = [
                    not_available if v is None else v for v in params[k]
                ]
            else:
                # TODO
                pass
        return params
