# pylint: disable=unused-argument, line-too-long
"""Test permission handling."""

from unittest.mock import patch

import pytest
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.core import HomeAssistant

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import build_token_file
from .const_integration import DOMAIN

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


@pytest.mark.parametrize(
    "base_config_entry",
    [{"shared_mailbox": "jane.doe@nomail.com"}],
    indirect=True,
)
@pytest.mark.parametrize("base_token", ["Mail.Read.Shared"], indirect=True)
async def test_shared_permissions(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test shared permissions."""
    assert "Mail.Read.Shared" in base_config_entry.runtime_data.permissions.permissions


@pytest.mark.parametrize(
    "base_config_entry",
    [{"shared_mailbox": "jane.doe@nomail.com", "enable_update": True}],
    indirect=True,
)
@pytest.mark.parametrize(
    "base_token", ["Mail.Read.Shared Mail.Send.Shared"], indirect=True
)
async def test_update_shared_permissions(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test shared update permissions."""
    assert "Mail.Send.Shared" in base_config_entry.runtime_data.permissions.permissions
    assert not hass.services.has_service(DOMAIN, "auto_reply_enable")
    assert not hass.services.has_service(DOMAIN, "auto_reply_disable")
    assert hass.services.has_service(NOTIFY_DOMAIN, "ms365_mail_test")


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
