"""Utilities for MS365 testing."""

from copy import deepcopy

from homeassistant.core import HomeAssistant

from ...helpers.mock_config_entry import MS365MockConfigEntry
from ..const_integration import BASE_SUBENTRY


async def update_subentry(hass: HomeAssistant, base_config_entry: MS365MockConfigEntry, options) -> None:
    """Update subentry options."""
    subentry = next(iter(base_config_entry.subentries.values()))
    result = await base_config_entry.start_subentry_reconfigure_flow(hass, subentry.subentry_id)

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        user_input=options,
    )
    await hass.async_block_till_done()


def create_subentries(subentry_options):
    """Create the subentries."""
    subentry = deepcopy(BASE_SUBENTRY)
    for item_key, item_value in subentry_options.items():
        subentry["data"][item_key] = item_value

    return [subentry]
