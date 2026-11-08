# pylint: disable=line-too-long, unused-argument
"""Test the config flow."""

from unittest.mock import MagicMock, patch

import pytest
from requests_mock import Mocker

from custom_components.ms365_mail.const import CONF_ENTITY_NAME
from custom_components.ms365_mail.integration.const_integration import (
    CONF_HAS_ATTACHMENT,
    CONF_HTML_BODY,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    Attachment,
    ImportanceLevel,
    Unread,
)
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from ..const import BASE_CONFIG_ENTRY, ENTITY_NAME
from ..helpers.mock_config_entry import MS365MockConfigEntry, config_entry_setup
from ..helpers.utils import build_token_url, get_schema_default, mock_token
from .const_integration import AUTH_CALLBACK_PATH_DEFAULT, DOMAIN, SHARED_TOKEN_PERMS
from .helpers_integration.mocks import MS365MOCKS


async def test_options_flow(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the options flow."""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)

    assert result["type"] is FlowResultType.ABORT


async def test_add_subentry(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the the additon of a subentry."""

    result = await hass.config_entries.subentries.async_init(
        (base_config_entry.entry_id, "mail"),
        context={"source": "user"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    subentity_name = "new"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            CONF_ENTITY_NAME: subentity_name,
            CONF_IMPORTANCE: ImportanceLevel.NONE,
            CONF_HAS_ATTACHMENT: Attachment.NONE,
            CONF_IS_UNREAD: Unread.NONE,
            CONF_HTML_BODY: True,
        },
    )

    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["unique_id"] == f"{DOMAIN}_{ENTITY_NAME}_{subentity_name}"
    assert CONF_IMPORTANCE not in result["data"]
    assert CONF_HAS_ATTACHMENT not in result["data"]
    assert CONF_IS_UNREAD not in result["data"]
    assert CONF_HTML_BODY in result["data"]
    assert result["data"][CONF_HTML_BODY] is True


async def test_modify_subentry(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test modifying a subentry."""

    subentry = next(iter(base_config_entry.subentries.values()))
    result = await base_config_entry.start_subentry_reconfigure_flow(hass, subentry.subentry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_IMPORTANCE) is None
    assert get_schema_default(schema, CONF_IS_UNREAD) is None

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        user_input={
            CONF_IMPORTANCE: ImportanceLevel.HIGH,
            CONF_IS_UNREAD: Unread.TRUE,
        },
    )
    await hass.async_block_till_done()

    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "reconfigure_successful"

    # Reload the entry to see changes
    entry = hass.config_entries.async_get_entry(base_config_entry.entry_id)
    updated_subentry = entry.subentries[subentry.subentry_id]

    assert updated_subentry.data[CONF_IMPORTANCE] == ImportanceLevel.HIGH
    assert updated_subentry.data[CONF_IS_UNREAD] == Unread.TRUE


async def test_modify_subentry_empty(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test modifying a subentry with empty data."""

    subentry = next(iter(base_config_entry.subentries.values()))
    result = await base_config_entry.start_subentry_reconfigure_flow(hass, subentry.subentry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_IMPORTANCE) is None
    assert get_schema_default(schema, CONF_IS_UNREAD) is None

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        user_input={
            CONF_IMPORTANCE: ImportanceLevel.NONE,
            CONF_HAS_ATTACHMENT: Attachment.NONE,
            CONF_IS_UNREAD: Unread.NONE,
        },
    )
    await hass.async_block_till_done()

    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "reconfigure_successful"

    # Reload the entry to see changes
    entry = hass.config_entries.async_get_entry(base_config_entry.entry_id)
    updated_subentry = entry.subentries[subentry.subentry_id]

    assert CONF_IMPORTANCE not in updated_subentry.data
    assert CONF_HAS_ATTACHMENT not in updated_subentry.data
    assert CONF_IS_UNREAD not in updated_subentry.data


async def test_shared_email_invalid(
    hass: HomeAssistant,
    requests_mock: Mocker,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test for invalid shared mailbox."""
    mock_token(requests_mock, SHARED_TOKEN_PERMS)
    MS365MOCKS.standard_mocks(requests_mock)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    email = "john@nomail.com"
    user_input = config_entry_setup(BASE_CONFIG_ENTRY, {"shared_mailbox": email})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=user_input,
    )

    with patch(
        f"custom_components.{DOMAIN}.classes.api.MS365CustomAccount",
        return_value=mock_account(email),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                "url": build_token_url(result, AUTH_CALLBACK_PATH_DEFAULT),
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    assert (
        f"Login email address '{email}' should not be entered as shared email address, config attribute removed"
        in caplog.text
    )


def mock_account(email):
    """Mock the account."""
    return MagicMock(is_authenticated=True, username=email, main_resource=email)
