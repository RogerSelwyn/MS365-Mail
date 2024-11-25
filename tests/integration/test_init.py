# pylint: disable=unused-argument
"""Test setup process."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant

from custom_components.ms365_mail.integration.const_integration import (
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    ImportanceLevel,
    Unread,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry


async def test_reload(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test for reload."""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as mock_async_reload:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_IMPORTANCE: ImportanceLevel.HIGH,
                CONF_IS_UNREAD: Unread.TRUE,
            },
        )

    assert mock_async_reload.called
