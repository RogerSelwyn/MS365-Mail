# pylint: disable=line-too-long, unused-argument
"""Test the config flow."""

from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from requests_mock import Mocker

from custom_components.ms365_mail.integration.const_integration import (
    CONF_HAS_ATTACHMENT,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    Attachment,
    ImportanceLevel,
    Unread,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import build_token_url, get_schema_default, mock_token
from .const_integration import (
    AUTH_CALLBACK_PATH_DEFAULT,
    BASE_CONFIG_ENTRY,
    DOMAIN,
    SHARED_TOKEN_PERMS,
)
from .helpers_integration.mocks import MS365MOCKS


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


async def test_shared_email_invalid(
    hass: HomeAssistant,
    requests_mock: Mocker,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test for invalid shared mailbox."""
    mock_token(requests_mock, SHARED_TOKEN_PERMS)
    MS365MOCKS.standard_mocks(requests_mock)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    user_input = deepcopy(BASE_CONFIG_ENTRY)
    email = "john@nomail.com"
    user_input["shared_mailbox"] = email
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
