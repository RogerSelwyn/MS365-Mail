"""Utilities for MS365 testing."""

from homeassistant.core import HomeAssistant

from ...helpers.mock_config_entry import MS365MockConfigEntry


async def update_options(
    hass: HomeAssistant, base_config_entry: MS365MockConfigEntry, options
) -> None:
    """Test the options flow"""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input=options,
    )
    await hass.async_block_till_done()
