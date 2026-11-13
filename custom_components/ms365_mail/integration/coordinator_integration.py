"""Sensor processing."""

from datetime import timedelta
import functools as ft
import logging

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from O365.utils.query import QueryBuilder  # pylint: disable=no-name-in-module, import-error

from ..const import ATTR_DATA, CONF_ENTITY_KEY, CONF_ENTITY_NAME, CONF_ENTITY_TYPE
from .const_integration import (
    ATTR_AUTOREPLIESSETTINGS,
    ATTR_STATE,
    CONF_DOWNLOAD_ATTACHMENTS,
    CONF_FOLDER,
    CONF_MAX_ITEMS,
    CONF_MS365_MAIL_FOLDER,
    CONF_QUERY,
    CONF_SAVE_ATTACHMENTS,
    SENSOR_AUTO_REPLY,
    SENSOR_EMAIL,
)
from .filemgmt_integration import (
    check_and_create_attachments_folder,
    save_attachments_to_disk,
)
from .sensor_integration import async_build_mail_query

_LOGGER = logging.getLogger(__name__)


class MS365EmailSensorCoordinator(DataUpdateCoordinator):
    """MS365 email sensor data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        subentry: ConfigSubentry,
        account,
        autoreply,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            # Name of the data. For logging purposes.
            name="MS365 Email",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._hass = hass
        self._entry = entry
        self.subentry = subentry
        self.account = account
        subentity_name = (
            f"_{subentry.data[CONF_ENTITY_NAME]}"
            if subentry.data[CONF_ENTITY_NAME] != entry.data[CONF_ENTITY_NAME]
            else ""
        )
        self._entity_name = f"{entry.data[CONF_ENTITY_NAME]}{subentity_name}"
        self.keys = []
        self._data = {}
        self._builder = QueryBuilder(protocol=account.protocol)

    async def _async_setup(self):
        """Do the initial setup of the entities."""
        self.keys = await self._async_email_sensors()
        return self.keys

    async def _async_email_sensors(self):
        if mail_folder := await self._async_get_mail_folder():
            name = f"{self._entity_name}_Mail"
            # Why is this like this. Legacy it uses the folder_id from Graph,
            # but the folder_id changes if the user changes the folder to monitor/
            # So better to use the non-changeble entity name.
            if self.subentry.data.get(CONF_SAVE_ATTACHMENTS):
                check_and_create_attachments_folder(self._hass)

            new_key = {
                CONF_ENTITY_KEY: name.lower(),
                CONF_UNIQUE_ID: name.lower(),
                CONF_MS365_MAIL_FOLDER: mail_folder,
                CONF_NAME: name,
                CONF_ENTITY_TYPE: SENSOR_EMAIL,
                CONF_QUERY: await async_build_mail_query(
                    self.subentry.data, self._builder
                ),
            }
            return [new_key]

        return []

    async def _async_get_mail_folder(self):
        """Get the configured folder."""
        mailbox = await self.hass.async_add_executor_job(self.account.mailbox)
        _LOGGER.debug("Get mail folder: %s", self._entry.data[CONF_ENTITY_NAME])
        if mail_folder_conf := self.subentry.data.get(CONF_FOLDER):
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

    async def _async_update_data(self):
        _LOGGER.debug(
            "Doing %s email update(s) for: %s", len(self.keys), self._entity_name
        )

        for key in self.keys:
            await self._async_email_update(key)

        return self._data

    async def _async_email_update(self, key):
        """Update code."""

        download_attachments = self.subentry.data.get(CONF_DOWNLOAD_ATTACHMENTS)
        save_attachments = self.subentry.data.get(CONF_SAVE_ATTACHMENTS)
        fetch_attachments = download_attachments or save_attachments
        max_items = self.subentry.data.get(CONF_MAX_ITEMS, 5)
        mail_folder = key[CONF_MS365_MAIL_FOLDER]
        entity_key = key[CONF_ENTITY_KEY]
        query = key[CONF_QUERY]

        data = await self.hass.async_add_executor_job(  # pylint: disable=no-member
            ft.partial(
                mail_folder.get_messages,
                limit=max_items,
                query=query,
                download_attachments=fetch_attachments,
            )
        )
        self._data[entity_key] = {
            ATTR_DATA: await self.hass.async_add_executor_job(list, data)
        }
        if save_attachments:
            await self.hass.async_add_executor_job(
                save_attachments_to_disk, self._hass, self._data[entity_key][ATTR_DATA]
            )


class MS365AutoReplySensorCoordinator(DataUpdateCoordinator):
    """MS365 autoreply sensor data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        account,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            # Name of the data. For logging purposes.
            name="MS365 Email",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._hass = hass
        self._entry = entry
        self.account = account
        self.keys = []
        self._data = {}
        self._entity_name = f"{entry.data[CONF_ENTITY_NAME]}"

    async def _async_setup(self):
        """Do the initial setup of the entities."""
        self.keys = await self._async_auto_reply_sensors()
        return self.keys

    async def _async_auto_reply_sensors(self):
        name = f"{self._entry.data[CONF_ENTITY_NAME]}_Autoreply"
        new_key = {
            CONF_ENTITY_KEY: name.lower(),
            CONF_UNIQUE_ID: name.lower(),
            CONF_NAME: name,
            CONF_ENTITY_TYPE: SENSOR_AUTO_REPLY,
        }

        return [new_key]

    async def _async_update_data(self):
        _LOGGER.debug(
            "Doing %s autoreply update(s) for: %s", len(self.keys), self._entity_name
        )

        for key in self.keys:
            await self._async_auto_reply_update(key)

        return self._data

    async def _async_auto_reply_update(self, key):
        """Update state."""
        entity_key = key[CONF_ENTITY_KEY]
        if data := await self.hass.async_add_executor_job(
            self.account.mailbox().get_settings
        ):
            self._data[entity_key] = {
                ATTR_STATE: data.automaticrepliessettings.status.value,
                ATTR_AUTOREPLIESSETTINGS: data.automaticrepliessettings,
            }
