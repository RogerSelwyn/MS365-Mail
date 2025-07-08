# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test main sensors testing."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from requests_mock import Mocker

from custom_components.ms365_mail.integration.const_integration import (
    Attachment,
    ImportanceLevel,
    Unread,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import check_entity_state, mock_call  # , utcnow
from .const_integration import URL
from .data_integration.state import (
    BASE_AUTOREPLY,
    BASE_MESSAGES,
    CHILD_MESSAGES,
    CLEAN_HTML_MESSAGES,
    SAFE_HTML_MESSAGES,
)
from .helpers_integration.mocks import MS365MOCKS
from .helpers_integration.utils_integration import update_options


async def test_get_data(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test get data."""
    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 1

    check_entity_state(hass, "sensor.test_mail", "2", BASE_MESSAGES)


@pytest.mark.parametrize(
    "base_config_entry",
    [{"enable_autoreply": True, "enable_update": True}],
    indirect=True,
)
@pytest.mark.parametrize(
    "base_token", ["Mail.Read Mail.Send MailboxSettings.ReadWrite"], indirect=True
)
async def test_get_autoreply(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test get data."""
    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 2

    check_entity_state(hass, "sensor.test_autoreply", "disabled", BASE_AUTOREPLY)


async def test_get_query_build(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test get data."""
    await update_options(hass, base_config_entry, {"body_contains": "body_text"})
    _check_filter(base_config_entry, "contains(body/content, 'body_text')")

    await update_options(hass, base_config_entry, {"subject_contains": "subject_text"})
    _check_filter(base_config_entry, "contains(subject, 'subject_text'")

    await update_options(hass, base_config_entry, {"subject_is": "subject_text"})
    _check_filter(base_config_entry, "subject eq 'subject_text'")

    await update_options(hass, base_config_entry, {"has_attachment": Attachment.TRUE})
    _check_filter(base_config_entry, "hasAttachments eq true")

    await update_options(hass, base_config_entry, {"from": "spam@nomail.com"})
    _check_filter(base_config_entry, "from/emailAddress/address eq 'spam@nomail.com'")

    await update_options(hass, base_config_entry, {"is_unread": Unread.TRUE})
    _check_filter(base_config_entry, "isRead eq false")

    await update_options(hass, base_config_entry, {"importance": ImportanceLevel.HIGH})
    _check_filter(base_config_entry, "importance eq 'High'")

    await update_options(hass, base_config_entry, {"html_body": True})
    _check_select(base_config_entry, "body")

    await update_options(hass, base_config_entry, {"show_body": True})
    _check_select(base_config_entry, "body")

    await update_options(hass, base_config_entry, {"download_attachments": True})
    _check_select(base_config_entry, "attachments")

    await update_options(hass, base_config_entry, {"save_attachments": True})
    _check_select(base_config_entry, "attachments")


async def test_run_update(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test running coordinator update."""
    coordinator = base_config_entry.runtime_data.coordinator
    with patch(
        "homeassistant.helpers.entity.Entity.async_write_ha_state"
    ) as mock_async_write_ha_state:
        await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert mock_async_write_ha_state.called


@pytest.mark.parametrize(
    "base_config_entry",
    [{"options": {"html_body": True}}],
    indirect=True,
)
async def test_safe_html(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test safe_html is working."""
    check_entity_state(hass, "sensor.test_mail", "2", SAFE_HTML_MESSAGES)


@pytest.mark.parametrize(
    "base_config_entry",
    [{"options": {"show_body": True}}],
    indirect=True,
)
async def test_show_body(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test safe_html is working."""
    check_entity_state(hass, "sensor.test_mail", "2", CLEAN_HTML_MESSAGES)


@pytest.mark.parametrize(
    "base_config_entry",
    [{"options": {"folder": "RootFolder/SubFolder"}}],
    indirect=True,
)
async def test_subfolder(
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test subfolder is working."""
    MS365MOCKS.standard_mocks(requests_mock)
    mock_call(requests_mock, URL.ROOTFOLDER, "rootfolder")
    mock_call(requests_mock, URL.CHILDFOLDER, "childfolder")
    mock_call(requests_mock, URL.CHILDMESSAGES, "child_messages")
    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    check_entity_state(hass, "sensor.test_mail", "1", CHILD_MESSAGES)


@pytest.mark.parametrize(
    "base_config_entry",
    [{"options": {"folder": "RootFolder/BadFolder"}}],
    indirect=True,
)
async def test_bad_subfolder(
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    caplog: pytest.LogCaptureFixture,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test subfolder is working."""
    MS365MOCKS.standard_mocks(requests_mock)
    mock_call(requests_mock, URL.ROOTFOLDER, "rootfolder")
    mock_call(requests_mock, URL.BADFOLDER, "badfolder")
    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    assert (
        "Folder - BadFolder - not found from test config entry - RootFolder/BadFolder - entity not created"
        in caplog.text
    )


def _check_filter(base_config_entry, filterdata):
    assert filterdata in str(base_config_entry.runtime_data.sensors[0]["query"].filters)


def _check_select(base_config_entry, selectdata):
    assert selectdata in base_config_entry.runtime_data.sensors[0]["query"].select
