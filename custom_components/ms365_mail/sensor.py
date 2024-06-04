"""Sensor processing."""

import logging

from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ENABLE_UPDATE, CONF_ENTITY_KEY, CONF_ENTITY_TYPE
from .helpers.config_entry import MS365ConfigEntry
from .integration.const_integration import (
    CONF_ENABLE_AUTOREPLY,
    PERM_MAILBOX_SETTINGS,
    SENSOR_AUTO_REPLY,
    SENSOR_EMAIL,
)
from .integration.mailsensor import MS365AutoReplySensor, MS365MailSensor
from .integration.schema_integration import (
    AUTO_REPLY_SERVICE_DISABLE_SCHEMA,
    AUTO_REPLY_SERVICE_ENABLE_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MS365 platform."""

    account = entry.runtime_data.account

    is_authenticated = account.is_authenticated
    if not is_authenticated:
        return False

    sensor_entities = _sensor_entities(entry)
    email_entities = _email_entities(entry)
    entities = sensor_entities + email_entities

    async_add_entities(entities, False)
    await _async_setup_register_services(entry)

    return True


def _sensor_entities(entry):
    return [
        MS365AutoReplySensor(
            entry.runtime_data.coordinator,
            entry,
            key[CONF_NAME],
            key[CONF_ENTITY_KEY],
            key[CONF_UNIQUE_ID],
        )
        for key in entry.runtime_data.sensors
        if key[CONF_ENTITY_TYPE] == SENSOR_AUTO_REPLY
    ]


def _email_entities(entry):
    return [
        MS365MailSensor(
            entry.runtime_data.coordinator,
            entry,
            key[CONF_NAME],
            key[CONF_ENTITY_KEY],
            key[CONF_UNIQUE_ID],
        )
        for key in entry.runtime_data.sensors
        if key[CONF_ENTITY_TYPE] == SENSOR_EMAIL
    ]


async def _async_setup_register_services(entry):
    perms = entry.runtime_data.permissions
    await _async_setup_mailbox_services(entry, perms)


async def _async_setup_mailbox_services(entry, perms):
    if not entry.data.get(CONF_ENABLE_UPDATE):
        return

    if not entry.data.get(CONF_ENABLE_AUTOREPLY):
        return

    platform = entity_platform.async_get_current_platform()
    if perms.validate_authorization(PERM_MAILBOX_SETTINGS):
        platform.async_register_entity_service(
            "auto_reply_enable",
            AUTO_REPLY_SERVICE_ENABLE_SCHEMA,
            "auto_reply_enable",
        )
        platform.async_register_entity_service(
            "auto_reply_disable",
            AUTO_REPLY_SERVICE_DISABLE_SCHEMA,
            "auto_reply_disable",
        )
