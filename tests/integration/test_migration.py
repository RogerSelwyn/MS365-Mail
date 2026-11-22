# pylint: disable=unused-argument
"""Test migration."""

import pytest
from requests_mock import Mocker

from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.ms365_mail.integration.setup_integration import async_migrate_entry

from ..const import BASE_CONFIG_ENTRY, ENTITY_NAME
from ..helpers.mock_config_entry import MS365MockConfigEntry, config_entry_setup
from ..integration.const_integration import BASE_SUBENTRY, DOMAIN
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

    inbox_unique_id = "Inbox_test"
    ar_unique_id = "Autoreply_test"
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
    assert ar_entity.previous_unique_id == ar_unique_id
    assert ar_entity.unique_id == "test_autoreply"
    assert ar_entity.config_subentry_id is None


async def test_migrate_v2_v21_reuses_existing_mail_subentry(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
):
    """Resume migration when the inbox subentry was already created."""
    entry = MS365MockConfigEntry(
        domain=DOMAIN,
        title=ENTITY_NAME,
        unique_id=DOMAIN,
        data=config_entry_setup(BASE_CONFIG_ENTRY),
        options={"legacy": True},
        version=2,
        minor_version=0,
    )
    entry.add_to_hass(hass)
    inbox = ConfigSubentry(**BASE_SUBENTRY)
    other = ConfigSubentry(
        data={**BASE_SUBENTRY["data"]},
        subentry_type=inbox.subentry_type,
        title="Other inbox",
        unique_id=f"{DOMAIN}_other_other",
    )
    hass.config_entries.async_add_subentry(entry, inbox)
    hass.config_entries.async_add_subentry(entry, other)

    legacy_entity = entity_registry.async_get_or_create(
        platform=DOMAIN,
        domain=Platform.SENSOR,
        unique_id="Inbox_test",
        config_entry=entry,
        object_id_base="test_mail",
    )
    other_entity = entity_registry.async_get_or_create(
        platform=DOMAIN,
        domain=Platform.SENSOR,
        unique_id="other_mail",
        config_entry=entry,
        config_subentry_id=other.subentry_id,
        object_id_base="other_mail",
    )

    for _ in range(2):
        await async_migrate_entry(hass, entry)
        assert (entry.version, entry.minor_version) == (2, 1)
        assert not entry.options
        assert dict(entry.subentries) == {
            inbox.subentry_id: inbox,
            other.subentry_id: other,
        }
        migrated = entity_registry.async_get(legacy_entity.entity_id)
        assert migrated.unique_id == "test_mail"
        assert migrated.config_subentry_id == inbox.subentry_id
        assert entity_registry.async_get(other_entity.entity_id) == other_entity
