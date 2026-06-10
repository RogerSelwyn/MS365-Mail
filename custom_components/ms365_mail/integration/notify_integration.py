"""Notification processing."""

import logging

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
    BaseNotificationService,
)

from ..classes.config_entry import MS365ConfigEntry
from ..const import CONF_ENTITY_NAME
from .const_integration import (
    ATTR_IMPORTANCE,
    ATTR_SENDER,
    CONF_ENTRY,
    PERM_MAIL_SEND,
)
from .schema_integration import NOTIFY_SERVICE_BASE_SCHEMA
from .utils_integration import (
    build_attachments,
    build_message,
    cleanup,
)

_LOGGER = logging.getLogger(__name__)


async def async_integration_get_service(hass, config, discovery_info=None):  # pylint: disable=unused-argument
    """Get the service."""
    if discovery_info is None or not hasattr(
        discovery_info[CONF_ENTRY], "runtime_data"
    ):  # pragma: no cover
        return

    entry: MS365ConfigEntry = discovery_info[CONF_ENTRY]
    account = entry.runtime_data.ha_account.account

    return MS365EmailService(account, entry)


class MS365EmailService(BaseNotificationService):
    """Implement the notification service for MS365."""

    def __init__(self, account, entry: MS365ConfigEntry):
        """Initialize the service."""
        self.account = account
        self._entry = entry

    @property
    def targets(self):
        """Targets property."""
        return {f"_{self._entry.data.get(CONF_ENTITY_NAME)}": ""}

    def send_message(self, message="", **kwargs):  # pragma: no cover
        """Send a message to a user."""
        _LOGGER.warning("Non async send_message unsupported")

    async def async_send_message(self, message="", **kwargs):
        """Send an async message to a user."""

        if not self._entry.runtime_data.permissions.validate_authorization(
            PERM_MAIL_SEND
        ):
            _LOGGER.error(
                "Not authorised to send mail - requires permission: %s",
                f"{PERM_MAIL_SEND}(.Shared)",
            )
            return

        data = kwargs.get(ATTR_DATA)
        if data is None:
            kwargs.pop(ATTR_DATA)

        NOTIFY_SERVICE_BASE_SCHEMA(kwargs)

        title = kwargs.get(ATTR_TITLE, "Notification from Home Assistant")

        if data and data.get(ATTR_TARGET, None):
            if isinstance(data.get(ATTR_TARGET), list):
                targets = data.get(ATTR_TARGET)
            else:
                targets = [data.get(ATTR_TARGET)]
        else:
            resp = await self.hass.async_add_executor_job(
                self.account.get_current_user_data
            )
            targets = [resp.mail]

        new_message = await self.hass.async_add_executor_job(self.account.new_message)
        message = await self.hass.async_add_executor_job(
            build_message, self.hass, data, message, new_message.attachments
        )
        cleanup_files = await self.hass.async_add_executor_job(
            build_attachments, self.hass, data, new_message.attachments
        )
        for target in targets:
            new_message.to.add(target)
        if data:
            if data.get(ATTR_SENDER, None):
                new_message.sender = data.get(ATTR_SENDER)
            if data.get(ATTR_IMPORTANCE, None):
                new_message.importance = data.get(ATTR_IMPORTANCE)
        new_message.subject = title
        new_message.body = message
        await self.hass.async_add_executor_job(new_message.send)

        cleanup(cleanup_files)
