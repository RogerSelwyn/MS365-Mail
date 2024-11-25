# pylint: disable=line-too-long, unused-argument
"""Test the config flow."""

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ms365_mail.integration.const_integration import (
    CONF_HAS_ATTACHMENT,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    Attachment,
    ImportanceLevel,
    Unread,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import get_schema_default


async def test_options_flow(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the options flow"""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_IMPORTANCE) is None
    assert get_schema_default(schema, CONF_IS_UNREAD) is None

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_IMPORTANCE: ImportanceLevel.HIGH,
            CONF_IS_UNREAD: Unread.TRUE,
        },
    )
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    assert result["result"] is True
    assert result["data"][CONF_IMPORTANCE] == ImportanceLevel.HIGH
    assert result["data"][CONF_IS_UNREAD] == Unread.TRUE


async def test_options_flow_empty(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the options flow"""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_IMPORTANCE) is None
    assert get_schema_default(schema, CONF_IS_UNREAD) is None

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_IMPORTANCE: ImportanceLevel.NONE,
            CONF_HAS_ATTACHMENT: Attachment.NONE,
            CONF_IS_UNREAD: Unread.NONE,
        },
    )
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert "result" in result
    print(result)
    assert result["result"] is True
    assert CONF_IMPORTANCE not in result["data"]
    assert CONF_HAS_ATTACHMENT not in result["data"]
    assert CONF_IS_UNREAD not in result["data"]
