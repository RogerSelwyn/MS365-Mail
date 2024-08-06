"""Do configuration setup."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery

from ..const import CONF_ENABLE_UPDATE
from .const_integration import CONF_ENTRY, DOMAIN, PLATFORMS
from .coordinator_integration import MS365SensorCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_do_setup(hass: HomeAssistant, entry: ConfigEntry, account):
    """Run the setup after we have everything configured."""

    _LOGGER.debug("Sensor setup - start")
    email_coordinator = MS365SensorCoordinator(hass, entry, account)
    await email_coordinator.async_config_entry_first_refresh()
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
    _LOGGER.debug("Email setup - finish")
    return email_coordinator, email_coordinator.keys, PLATFORMS
