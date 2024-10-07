"""Sensor processing."""

import functools as ft
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..const import (
    ATTR_DATA,
    CONF_ENTITY_KEY,
    CONF_ENTITY_NAME,
    CONF_ENTITY_TYPE,
)
from ..helpers.utils import build_entity_id
from .const_integration import (
    ATTR_AUTOREPLIESSETTINGS,
    ATTR_STATE,
    CONF_DOWNLOAD_ATTACHMENTS,
    CONF_ENABLE_AUTOREPLY,
    CONF_FOLDER,
    CONF_MAX_ITEMS,
    CONF_MS365_MAIL_FOLDER,
    CONF_QUERY,
    ENTITY_ID_FORMAT_SENSOR,
    SENSOR_AUTO_REPLY,
    SENSOR_EMAIL,
)
from .sensor_integration import async_build_mail_query

_LOGGER = logging.getLogger(__name__)


class MS365SensorCoordinator(DataUpdateCoordinator):
    """MS365 sensor data update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, account):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="MS365 Email",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._hass = hass
        self._entry = entry
        self._account = account
        self._entity_name = entry.data[CONF_ENTITY_NAME]
        self.keys = []
        self._data = {}

    async def _async_setup(self):
        """Do the initial setup of the entities."""
        email_keys = await self._async_email_sensors()
        auto_reply_entities = await self._async_auto_reply_sensors()
        self.keys = email_keys + auto_reply_entities
        return self.keys

    async def _async_email_sensors(self):
        keys = []
        name = f"{self._entry.data[CONF_ENTITY_NAME]}_mail"
        if mail_folder := await self._async_get_mail_folder():
            new_key = {
                CONF_ENTITY_KEY: build_entity_id(
                    self.hass, ENTITY_ID_FORMAT_SENSOR, name
                ),
                CONF_UNIQUE_ID: f"{mail_folder.folder_id}_{self._entity_name}",
                CONF_MS365_MAIL_FOLDER: mail_folder,
                CONF_NAME: name,
                CONF_ENTITY_TYPE: SENSOR_EMAIL,
                CONF_QUERY: await async_build_mail_query(
                    self._hass, mail_folder, self._entry.options
                ),
            }

            keys.append(new_key)
        return keys

    async def _async_get_mail_folder(self):
        """Get the configured folder."""
        mailbox = await self.hass.async_add_executor_job(self._account.mailbox)
        _LOGGER.debug("Get mail folder: %s", self._entry.data[CONF_ENTITY_NAME])
        if mail_folder_conf := self._entry.options.get(CONF_FOLDER):
            return await self._async_get_configured_mail_folder(
                mail_folder_conf, mailbox
            )

        return await self.hass.async_add_executor_job(mailbox.inbox_folder)

    async def _async_get_configured_mail_folder(self, mail_folder_conf, mailbox):
        mail_folder = mailbox
        _LOGGER.debug("Get folder %s - start", mail_folder_conf)

        for folder in mail_folder_conf.split("/"):
            mail_folder = await self.hass.async_add_executor_job(
                ft.partial(
                    mail_folder.get_folder,
                    folder_name=folder,
                )
            )
            _LOGGER.debug("Get folder %s - process - %s", mail_folder_conf, mail_folder)
            if not mail_folder:
                _LOGGER.error(
                    "Folder - %s - not found from %s config entry - %s - entity not created",
                    folder,
                    self._entity_name,
                    mail_folder_conf,
                )
                return None

        _LOGGER.debug("Get folder %s - finish ", mail_folder_conf)
        return mail_folder

    async def _async_auto_reply_sensors(self):
        keys = []
        if self._entry.data[CONF_ENABLE_AUTOREPLY]:
            name = f"{self._entry.data[CONF_ENTITY_NAME]}_autoreply"
            new_key = {
                CONF_ENTITY_KEY: build_entity_id(
                    self.hass, ENTITY_ID_FORMAT_SENSOR, name
                ),
                CONF_UNIQUE_ID: name,
                CONF_NAME: name,
                CONF_ENTITY_TYPE: SENSOR_AUTO_REPLY,
            }

            keys.append(new_key)
        return keys

    async def _async_update_data(self):
        _LOGGER.debug(
            "Doing %s email update(s) for: %s", len(self.keys), self._entity_name
        )

        for key in self.keys:
            entity_type = key[CONF_ENTITY_TYPE]
            if entity_type == SENSOR_EMAIL:
                await self._async_email_update(key)
            elif entity_type == SENSOR_AUTO_REPLY:
                await self._async_auto_reply_update(key)

        return self._data

    async def _async_email_update(self, key):
        """Update code."""

        download_attachments = self._entry.options.get(CONF_DOWNLOAD_ATTACHMENTS)
        max_items = self._entry.options.get(CONF_MAX_ITEMS, 5)
        mail_folder = key[CONF_MS365_MAIL_FOLDER]
        entity_key = key[CONF_ENTITY_KEY]
        query = key[CONF_QUERY]

        data = await self.hass.async_add_executor_job(  # pylint: disable=no-member
            ft.partial(
                mail_folder.get_messages,
                limit=max_items,
                query=query,
                download_attachments=download_attachments,
            )
        )
        self._data[entity_key] = {
            ATTR_DATA: await self.hass.async_add_executor_job(list, data)
        }

    async def _async_auto_reply_update(self, key):
        """Update state."""
        entity_key = key[CONF_ENTITY_KEY]
        if data := await self.hass.async_add_executor_job(
            self._account.mailbox().get_settings
        ):
            self._data[entity_key] = {
                ATTR_STATE: data.automaticrepliessettings.status.value,
                ATTR_AUTOREPLIESSETTINGS: data.automaticrepliessettings,
            }
