"""Permissions processes for mail."""

from ..classes.permissions import BasePermissions
from ..const import (
    CONF_ENABLE_UPDATE,
    CONF_SHARED_MAILBOX,
    PERM_OFFLINE_ACCESS,
    PERM_SHARED,
    PERM_USER_READ,
)
from .const_integration import (
    CONF_ENABLE_AUTOREPLY,
    PERM_MAIL_READ,
    PERM_MAIL_SEND,
    PERM_MAILBOX_SETTINGS,
)


class Permissions(BasePermissions):
    """Class in support of building permission sets."""

    def __init__(self, hass, config):
        """Initialise the class."""
        super().__init__(hass, config)

        self._enable_autoreply = self._config.get(CONF_ENABLE_AUTOREPLY, False)
        self._shared = PERM_SHARED if config.get(CONF_SHARED_MAILBOX) else ""
        self._enable_update = self._config.get(CONF_ENABLE_UPDATE, False)

    @property
    def requested_permissions(self):
        """Return the required scope."""
        if not self._requested_permissions:
            self._requested_permissions = [PERM_OFFLINE_ACCESS, PERM_USER_READ]
            self._build_email_permissions()
            self._build_autoreply_permissions()

        return self._requested_permissions

    def _build_email_permissions(self):
        self._requested_permissions.append(PERM_MAIL_READ + self._shared)
        if self._enable_update:
            self._requested_permissions.append(PERM_MAIL_SEND + self._shared)

    def _build_autoreply_permissions(self):
        if self._enable_autoreply:
            self._requested_permissions.append(PERM_MAILBOX_SETTINGS)
