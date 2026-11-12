# pylint: disable=unused-argument
"""Test migration."""

import pytest
from requests_mock import Mocker

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..const import BASE_CONFIG_ENTRY, ENTITY_NAME
from ..helpers.mock_config_entry import MS365MockConfigEntry, config_entry_setup
from ..integration.const_integration import DOMAIN
from .helpers_integration.mocks import MS365MOCKS


@pytest.mark.parametrize("base_token", ["Mail.Read Mail.Send MailboxSettings.ReadWrite"], indirect=True)
async def test_migrate_v2_v21(
    hass: HomeAssistant,
    base_token,
    requests_mock: Mocker,
    caplog: pytest.LogCaptureFixture,
    entity_registry: er.EntityRegistry,
):
    """Test v2.1 migrate."""
    data = config_entry_setup(BASE_CONFIG_ENTRY, base_attributes={"enable_autoreply": True})
    options = None

    entry = MS365MockConfigEntry(
        domain=DOMAIN,
        title=ENTITY_NAME,
        unique_id=DOMAIN,
        data=data,
        options=options,
        version=2,
        minor_version=0,
    )

    entry.add_to_hass(hass)

    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    inbox_unique_id = "Inbox_test"
    ar_unique_id = "test_autoreply"
    entity_registry.async_get_or_create(
        platform=DOMAIN,
        domain=Platform.SENSOR,
        unique_id=inbox_unique_id,
        config_entry=entry,
        object_id_base="test_mail",
    )
    entity_registry.async_get_or_create(
        platform=DOMAIN,
        domain=Platform.SENSOR,
        unique_id=ar_unique_id,
        config_entry=entry,
        object_id_base="test_autoreply",
    )
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)

    MS365MOCKS.standard_mocks(requests_mock)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    assert len(entities) == 2
    inbox_entity = entity_registry.async_get("sensor.test_mail")
    assert inbox_entity.previous_unique_id == inbox_unique_id
    assert inbox_entity.unique_id == "test_mail"
    assert inbox_entity.config_subentry_id is not None
    ar_entity = entity_registry.async_get("sensor.test_autoreply")
    assert ar_entity.previous_unique_id is None
    assert ar_entity.unique_id == ar_unique_id
    assert ar_entity.config_subentry_id is None
