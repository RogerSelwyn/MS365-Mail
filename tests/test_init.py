# pylint: disable=unused-argument
"""Test setup process."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from oauthlib.oauth2.rfc6749.errors import InvalidClientError
from requests_mock import Mocker

from .helpers.mock_config_entry import MS365MockConfigEntry
from .integration.const_integration import FULL_INIT_ENTITY_NO
from .integration.helpers_integration.mocks import MS365MOCKS


async def test_full_init(
    hass: HomeAssistant,
    base_config_entry: MS365MockConfigEntry,
    base_token,
    requests_mock: Mocker,
    entity_registry: er.EntityRegistry,
):
    """Test full MS365 initialisation."""
    MS365MOCKS.standard_mocks(requests_mock)

    base_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(base_config_entry.entry_id)
    assert hasattr(base_config_entry.runtime_data, "options")

    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == FULL_INIT_ENTITY_NO


async def test_invalid_client_1(
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test an invalid client."""
    MS365MOCKS.standard_mocks(requests_mock)
    base_config_entry.add_to_hass(hass)

    with patch(
        "O365.Account.get_current_user",
        side_effect=InvalidClientError(description="client secret expired"),
    ):
        await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()
    assert "Client Secret expired for account" in caplog.text


async def test_invalid_client_2(
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test an invalid client."""
    MS365MOCKS.standard_mocks(requests_mock)
    base_config_entry.add_to_hass(hass)

    with patch(
        "O365.Account.get_current_user",
        side_effect=InvalidClientError(description="token error"),
    ):
        await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()
    assert "Token error for account" in caplog.text
