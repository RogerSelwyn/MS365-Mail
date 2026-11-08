"""Configuration flow for the skyq platform."""

from copy import deepcopy
from typing import Any

import probatio

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
import homeassistant.helpers.config_validation as cv

from ..classes.config_entry import MS365ConfigEntry
from ..const import CONF_ENABLE_UPDATE, CONF_ENTITY_NAME, CONF_SHARED_MAILBOX
from .const_integration import (
    CONF_ENABLE_AUTOREPLY,
    CONF_HAS_ATTACHMENT,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    DOMAIN,
    SUBENTRY_MAIL,
    Attachment,
    ImportanceLevel,
    Unread,
)
from .schema_integration import MAIL_FOLDER_SCHEMA

INTEGRATION_CONFIG_VERSION = 2
INRTEGRATION_CONFIG_MINOR_VERSION = 1


def integration_reconfigure_schema(entry_data):
    """Extend the schame with integration specific attributes."""
    return {
        probatio.Optional(
            CONF_ENABLE_UPDATE, default=entry_data[CONF_ENABLE_UPDATE]
        ): cv.boolean,
        probatio.Optional(
            CONF_SHARED_MAILBOX,
            description={"suggested_value": entry_data.get(CONF_SHARED_MAILBOX, None)},
        ): cv.string,
        probatio.Optional(
            CONF_ENABLE_AUTOREPLY, default=entry_data[CONF_ENABLE_AUTOREPLY]
        ): cv.boolean,
    }


def integration_validate_schema(user_input):  # pylint: disable=unused-argument
    """Validate the user input."""
    return {}


def integration_subentry_flows():
    """Provide the subentry flows."""
    return {SUBENTRY_MAIL: MailSubentryFlow}


def subentry_setup(name):
    """Create basic subentry."""
    return [
        {
            "data": {CONF_ENTITY_NAME: name},
            "subentry_type": SUBENTRY_MAIL,
            "title": name,
            "unique_id": f"{DOMAIN}_{name}_{name}",
        }
    ]


class MailSubentryFlow(ConfigSubentryFlow):
    """Add and change a mail folder."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        config_entry = self._get_entry()

        if user_input:
            if user_input.get(CONF_IS_UNREAD) == Unread.NONE:
                del user_input[CONF_IS_UNREAD]
            if user_input.get(CONF_HAS_ATTACHMENT) == Attachment.NONE:
                del user_input[CONF_HAS_ATTACHMENT]
            if user_input.get(CONF_IMPORTANCE) == ImportanceLevel.NONE:
                del user_input[CONF_IMPORTANCE]
            return self.async_create_entry(
                title=user_input[CONF_ENTITY_NAME],
                unique_id=f"{DOMAIN}_{config_entry.data[CONF_ENTITY_NAME]}_{user_input[CONF_ENTITY_NAME]}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(MAIL_FOLDER_SCHEMA),
            description_placeholders={
                CONF_ENTITY_NAME: config_entry.data[CONF_ENTITY_NAME]
            },
            errors=errors,
            last_step=True,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Change an existing mail folder."""
        entry = self._get_entry()
        subentry = self._get_reconfigure_subentry()

        if user_input:
            user_input[CONF_ENTITY_NAME] = subentry.data[CONF_ENTITY_NAME]
            if user_input.get(CONF_IS_UNREAD) == Unread.NONE:
                del user_input[CONF_IS_UNREAD]
            if user_input.get(CONF_HAS_ATTACHMENT) == Attachment.NONE:
                del user_input[CONF_HAS_ATTACHMENT]
            if user_input.get(CONF_IMPORTANCE) == ImportanceLevel.NONE:
                del user_input[CONF_IMPORTANCE]
            if user_input == subentry.data:
                return self.async_update_and_abort(
                    entry, subentry, data_updates=user_input
                )
            return self.async_update_reload_and_abort(
                entry, subentry, data_updates=user_input
            )

        data_schema = deepcopy(MAIL_FOLDER_SCHEMA)
        del data_schema[CONF_ENTITY_NAME]
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                probatio.Schema(data_schema), subentry.data
            ),
            description_placeholders={
                CONF_ENTITY_NAME: subentry.data[CONF_ENTITY_NAME]
            },
        )


class MS365OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for MS365."""

    def __init__(self, entry: MS365ConfigEntry) -> None:
        """Initialize MS365 options flow."""

    async def async_step_init(
        self,
        user_input=None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Set up the option flow."""

        return self.async_abort(reason="use_subentry")
