"""Implement a base class for audit loggers."""
from typing import Optional
import abc

from audit_logger import AuditLoggerConfig


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
    def log(self, **kwargs) -> dict:
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
