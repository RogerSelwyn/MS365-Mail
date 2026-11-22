"""Do configuration setup."""

import logging

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery, entity_registry as er

from ..const import CONF_ENABLE_UPDATE, CONF_ENTITY_NAME
from .const_integration import (
    CONF_ENABLE_AUTOREPLY,
    CONF_ENTRY,
    DOMAIN,
    PLATFORMS,
    SUBENTRY_MAIL,
)
from .coordinator_integration import (
    MS365AutoReplySensorCoordinator,
    MS365EmailSensorCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def async_do_setup(hass: HomeAssistant, entry: ConfigEntry, account):
    """Run the setup after we have everything configured."""

    _LOGGER.debug("Sensor setup - start")
    coordinators, keys = await _async_setup_coordinators(
        hass,
        account,
        entry,
    )
    _LOGGER.debug("Email setup - finish")
    return coordinators, keys, PLATFORMS


async def _async_setup_coordinators(hass: HomeAssistant, account, entry: ConfigEntry):
    coordinators = []
    keys = []
    autoreply = True
    for subentry in entry.get_subentries_of_type(SUBENTRY_MAIL):
        email_coordinator = MS365EmailSensorCoordinator(
            hass, entry, subentry, account, autoreply
        )
        await email_coordinator.async_config_entry_first_refresh()
        coordinators.append(email_coordinator)
        keys.append(email_coordinator.keys)

    if entry.data[CONF_ENABLE_AUTOREPLY]:
        autoreply_coordinator = MS365AutoReplySensorCoordinator(
            hass,
            entry,
            account,
        )
        await autoreply_coordinator.async_config_entry_first_refresh()
        coordinators.append(autoreply_coordinator)
        keys.append(autoreply_coordinator.keys)

    return coordinators, keys


async def async_extra_platform_setup(hass: HomeAssistant, entry: ConfigEntry):
    """Create notify platform."""

    if entry.data[CONF_ENABLE_UPDATE]:
        hass.async_create_task(
            discovery.async_load_platform(
                hass,
                "notify",
                DOMAIN,
                {CONF_ENTRY: entry},
                {},
            )
        )


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Migrate the integration specific entry."""
    if entry.version != 2 or entry.minor_version != 0:
        return

    name = entry.data[CONF_ENTITY_NAME]
    subentry_unique_id = f"{DOMAIN}_{name}_{name}"
    subentry = next(
        (
            existing
            for existing in entry.subentries.values()
            if existing.unique_id == subentry_unique_id
        ),
        None,
    )
    if subentry is None:
        data = dict(entry.options)
        data[CONF_ENTITY_NAME] = name
        subentry = ConfigSubentry(
            data=data,
            subentry_type=SUBENTRY_MAIL,
            title=name,
            unique_id=subentry_unique_id,
        )
        hass.config_entries.async_add_subentry(entry, subentry)

    entity_registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    for entity in entities:
        if entity.config_subentry_id not in (None, subentry.subentry_id):
            continue
        if "autoreply" not in entity.unique_id.lower():
            unique_id = f"{entry.data[CONF_ENTITY_NAME]}_mail".lower()
            entity_registry.async_update_entity(
                entity.entity_id,
                new_unique_id=unique_id,
                config_subentry_id=subentry.subentry_id,
            )
        else:
            unique_id = f"{entry.data[CONF_ENTITY_NAME]}_autoreply".lower()
            entity_registry.async_update_entity(
                entity.entity_id,
                new_unique_id=unique_id,
            )
    hass.config_entries.async_update_entry(
        entry,
        options={},
        version=2,
        minor_version=1,
    )
