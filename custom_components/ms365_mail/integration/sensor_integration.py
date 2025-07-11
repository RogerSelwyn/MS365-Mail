"""MS365 mail sensors."""

import datetime
import logging
from operator import itemgetter

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from O365 import mailbox  # pylint: disable=no-name-in-module
from O365.utils.query import (  # pylint: disable=no-name-in-module, import-error
    QueryBuilder,
)

from ..classes.config_entry import MS365ConfigEntry
from ..classes.entity import MS365Entity
from ..const import (
    ATTR_DATA,
    CONF_ENABLE_UPDATE,
    CONF_ENTITY_KEY,
    CONF_ENTITY_TYPE,
    DATETIME_FORMAT,
)
from ..helpers.utils import clean_html
from .const_integration import (
    ATTR_AUTOREPLIESSETTINGS,
    ATTR_END,
    ATTR_EXTERNAL_AUDIENCE,
    ATTR_EXTERNALREPLY,
    ATTR_INTERNALREPLY,
    ATTR_START,
    ATTR_STATE,
    CONF_BODY_CONTAINS,
    CONF_DOWNLOAD_ATTACHMENTS,
    CONF_ENABLE_AUTOREPLY,
    CONF_HAS_ATTACHMENT,
    CONF_HTML_BODY,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    CONF_MAIL_FROM,
    CONF_SAVE_ATTACHMENTS,
    CONF_SHOW_BODY,
    CONF_SUBJECT_CONTAINS,
    CONF_SUBJECT_IS,
    PERM_MAILBOX_SETTINGS,
    SENSOR_AUTO_REPLY,
    SENSOR_EMAIL,
    Attachment,
    Unread,
)
from .schema_integration import (
    AUTO_REPLY_SERVICE_DISABLE_SCHEMA,
    AUTO_REPLY_SERVICE_ENABLE_SCHEMA,
)
from .utils_integration import get_email_attributes

_LOGGER = logging.getLogger(__name__)


async def async_integration_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MS365 platform."""

    sensor_entities = await _async_sensor_entities(entry, hass)
    email_entities = _email_entities(entry)
    entities = sensor_entities + email_entities

    async_add_entities(entities, False)
    await _async_setup_register_services(entry)

    return True


async def _async_sensor_entities(entry, hass):
    entities = [
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
    for entity in entities:
        await entity.async_init(hass)
    return entities


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
            "async_auto_reply_enable",
        )
        platform.async_register_entity_service(
            "auto_reply_disable",
            AUTO_REPLY_SERVICE_DISABLE_SCHEMA,
            "async_auto_reply_disable",
        )


class MS365MailSensor(MS365Entity, SensorEntity):
    """MS365 generic Mail Sensor class."""

    _attr_translation_key = "mail"

    def __init__(
        self, coordinator, entry: MS365ConfigEntry, name, entity_id, unique_id
    ):
        """Initialise the MS365 Sensor."""
        super().__init__(coordinator, entry, name, entity_id, unique_id)
        download_attachments = entry.options.get(CONF_DOWNLOAD_ATTACHMENTS)
        save_attachments = entry.options.get(CONF_SAVE_ATTACHMENTS)
        self._fetch_attachments = download_attachments or save_attachments
        self._html_body = entry.options.get(CONF_HTML_BODY)
        self._show_body = entry.options.get(CONF_SHOW_BODY)
        self._state = None
        self._extra_attributes = None
        self._update_status()

    @property
    def native_value(self):
        """Sensor state."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Device state attributes."""
        return self._extra_attributes

    def _handle_coordinator_update(self) -> None:
        self._update_status()
        self.async_write_ha_state()

    def _update_status(self) -> None:
        data = self.coordinator.data[self.entity_key][ATTR_DATA]
        attrs = self._get_attributes(data)
        attrs.sort(key=itemgetter("received"), reverse=True)
        self._state = len(attrs)
        self._extra_attributes = {ATTR_DATA: attrs}

    def _get_attributes(self, data):
        return [
            get_email_attributes(
                x, self._fetch_attachments, self._html_body, self._show_body
            )
            for x in data
        ]


class MS365AutoReplySensor(MS365Entity, SensorEntity):
    """MS365 Auto Reply sensor processing."""

    _attr_translation_key = "auto_reply"

    def __init__(
        self, coordinator, entry: MS365ConfigEntry, name, entity_id, unique_id
    ):
        """Initialise the Auto reply Sensor."""
        super().__init__(coordinator, entry, name, entity_id, unique_id)
        self._entry = entry
        self._account = self._entry.runtime_data.ha_account.account
        self.mailbox = None

    async def async_init(self, hass):
        """async initialise."""
        self.mailbox = await hass.async_add_executor_job(self._account.mailbox)

    @property
    def native_value(self):
        """Sensor state."""
        return self.coordinator.data[self.entity_key][ATTR_STATE]

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        ars = self.coordinator.data[self.entity_key][ATTR_AUTOREPLIESSETTINGS]
        return {
            ATTR_INTERNALREPLY: clean_html(ars.internal_reply_message),
            ATTR_EXTERNALREPLY: clean_html(ars.external_reply_message),
            ATTR_EXTERNAL_AUDIENCE: ars.external_audience.value,
            ATTR_START: ars.scheduled_startdatetime.strftime(DATETIME_FORMAT),
            ATTR_END: ars.scheduled_enddatetime.strftime(DATETIME_FORMAT),
        }

    async def async_auto_reply_enable(
        self,
        external_reply,
        internal_reply,
        start=None,
        end=None,
        external_audience=mailbox.ExternalAudience.ALL,
    ):
        """Enable out of office autoreply."""
        self._validate_autoreply_permissions()

        await self.hass.async_add_executor_job(
            self.mailbox.set_automatic_reply,
            internal_reply,
            external_reply,
            start,
            end,
            external_audience,
        )

    async def async_auto_reply_disable(self):
        """Disable out of office autoreply."""
        self._validate_autoreply_permissions()

        await self.hass.async_add_executor_job(self.mailbox.set_disable_reply)

    def _validate_autoreply_permissions(self):
        return self._validate_permissions(
            PERM_MAILBOX_SETTINGS,
            "Not authorised to update auto reply - requires permission: "
            + f"{PERM_MAILBOX_SETTINGS}",
        )


async def _async_build_base_query(sensor_conf, builder):
    """Build base query for mail."""
    download_attachments = sensor_conf.get(CONF_DOWNLOAD_ATTACHMENTS)
    save_attachments = sensor_conf.get(CONF_SAVE_ATTACHMENTS)
    fetch_attachments = download_attachments or save_attachments
    show_body = sensor_conf.get(CONF_SHOW_BODY)
    html_body = sensor_conf.get(CONF_HTML_BODY)
    query = builder.select(
        "sender",
        "from",
        "subject",
        "receivedDateTime",
        "toRecipients",
        "ccRecipients",
        "has_attachments",
        "importance",
        "is_read",
        "flag",
    )
    if show_body or html_body:
        query = query & builder.select(
            "body",
        )
    if fetch_attachments:
        query = query & builder.select(
            "attachments",
        )
    return query


async def async_build_mail_query(sensor_conf, builder: QueryBuilder):
    """Build query for mail sensor."""
    query = await _async_build_base_query(sensor_conf, builder)
    query = query & builder.orderby(("receivedDateTime", False))

    body_contains = sensor_conf.get(CONF_BODY_CONTAINS)
    subject_contains = sensor_conf.get(CONF_SUBJECT_CONTAINS)
    subject_is = sensor_conf.get(CONF_SUBJECT_IS)
    if not sensor_conf.get(CONF_HAS_ATTACHMENT):
        has_attachment = None
    else:
        has_attachment = sensor_conf[CONF_HAS_ATTACHMENT] == Attachment.TRUE

    importance = sensor_conf.get(CONF_IMPORTANCE)
    email_from = sensor_conf.get(CONF_MAIL_FROM)
    if not sensor_conf.get(CONF_IS_UNREAD):
        is_unread = None
    else:
        is_unread = sensor_conf[CONF_IS_UNREAD] == Unread.TRUE

    if (
        body_contains is not None
        or subject_contains is not None
        or subject_is is not None
        or has_attachment is not None
        or importance is not None
        or email_from is not None
        or is_unread is not None
    ):
        query = query & builder.greater_equal(
            "receivedDateTime", datetime.datetime(1900, 5, 1)
        )

    query = _add_to_query(query, builder, "contains", "body", body_contains)
    query = _add_to_query(query, builder, "contains", "subject", subject_contains)
    query = _add_to_query(query, builder, "equals", "subject", subject_is)
    query = _add_to_query(query, builder, "equals", "hasAttachments", has_attachment)
    query = _add_to_query(query, builder, "equals", "from", email_from)
    query = _add_to_query(query, builder, "equals", "IsRead", not is_unread, is_unread)
    query = _add_to_query(query, builder, "equals", "importance", importance)

    return query


def _add_to_query(
    query,
    builder: QueryBuilder,
    qtype,
    attribute_name,
    attribute_value,
    check_value=True,
):
    if attribute_value is None or check_value is None:
        return query

    if qtype == "ge":
        query = query & builder.greater_equal(attribute_name, attribute_value)

    if qtype == "contains":
        query = query & builder.contains(attribute_name, attribute_value)
    if qtype == "equals":
        query = query & builder.equals(attribute_name, attribute_value)

    return query
