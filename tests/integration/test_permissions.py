# pylint: disable=unused-argument, line-too-long
"""Test permission handling."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import build_token_file

### Note that permissions code also supports Presence/Calendar which are not present in the mail integration


async def test_base_permissions(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test base permissions."""
    assert "Mail.Read" in base_config_entry.runtime_data.permissions.permissions


async def test_update_permissions(
    hass: HomeAssistant,
    setup_update_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test update permissions."""
    assert "Mail.Send" in base_config_entry.runtime_data.permissions.permissions


async def test_missing_permissions(
    tmp_path,
    hass: HomeAssistant,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
):
    """Test for missing permissions."""
    build_token_file(tmp_path, "")

    base_config_entry.add_to_hass(hass)
    with patch(
        "homeassistant.helpers.issue_registry.async_create_issue"
    ) as mock_async_create_issue:
        await hass.config_entries.async_setup(base_config_entry.entry_id)

    assert "Minimum required permissions: 'Mail.Read'" in caplog.text
    assert mock_async_create_issue.called
