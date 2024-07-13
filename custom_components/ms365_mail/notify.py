"""Notification processing."""

from homeassistant.core import HomeAssistant

from .integration.notify_integration import async_integration_get_service


async def async_get_service(hass: HomeAssistant, config, discovery_info=None):  # pylint: disable=unused-argument
    """Get the service."""
    return await async_integration_get_service(hass, config, discovery_info)
