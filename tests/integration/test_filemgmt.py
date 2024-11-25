# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test main sensors testing."""

import pytest
from homeassistant.core import HomeAssistant
from requests_mock import Mocker

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import check_entity_state
from ..integration.helpers_integration.mocks import MS365MOCKS
from .data_integration.state import ATTACHMENT_MESSAGES


@pytest.mark.parametrize(
    "base_config_entry",
    [{"options": {"save_attachments": True}}],
    indirect=True,
)
async def test_attachment_download(
    tmp_path,
    adjust_config_dir,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test safe_html is working."""
    MS365MOCKS.standard_mocks(requests_mock)
    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    check_entity_state(hass, "sensor.test_mail", "2", ATTACHMENT_MESSAGES)
    attachment_folder = tmp_path / "ms365_storage/attachments"
    attachment_file = attachment_folder / "attachment1---test.jpg"
    assert attachment_file.is_file()
    assert len(list(attachment_folder.glob("*"))) == 1

    coordinator = base_config_entry.runtime_data.coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert attachment_file.is_file()
    assert len(list(attachment_folder.glob("*"))) == 1
