"""Do configuration setup."""

import logging

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery, entity_registry as er

from ..const import CONF_ENABLE_UPDATE, CONF_ENTITY_NAME
from .const_integration import CONF_ENTRY, DOMAIN, PLATFORMS, SUBENTRY_MAIL
from .coordinator_integration import MS365SensorCoordinator

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
        email_coordinator = MS365SensorCoordinator(
            hass, entry, subentry, account, autoreply
        )
        await email_coordinator.async_config_entry_first_refresh()
        coordinators.append(email_coordinator)
        keys.append(email_coordinator.keys)
        autoreply = False
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
    if entry.version == 2 and entry.minor_version == 0:
        name = entry.data[CONF_ENTITY_NAME]
        data = dict(entry.options)
        data[CONF_ENTITY_NAME] = name
        subentry = ConfigSubentry(
            data=data,
            subentry_type=SUBENTRY_MAIL,
            title=name,
            unique_id=f"{DOMAIN}_{name}_{name}",
        )
        hass.config_entries.async_add_subentry(entry, subentry)

        for key in entry.subentries:
            new_subentry_id = key
        entity_registry = er.async_get(hass)
        entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        for entity in entities:
            if "autoreply" not in entity.unique_id:
                unique_id = f"{entry.data[CONF_ENTITY_NAME]}_mail"
                entity_registry.async_update_entity(
                    entity.entity_id,
                    new_unique_id=unique_id,
                    config_subentry_id=new_subentry_id,
                )

        hass.config_entries.async_update_entry(
            entry,
            options={},
            version=2,
            minor_version=1,
        )
