"""Configuration flow for the skyq platform."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import (
    config_entries,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import BooleanSelector

from ..const import CONF_ENABLE_UPDATE, CONF_ENTITY_NAME, CONF_SHARED_MAILBOX
from ..helpers.config_entry import MS365ConfigEntry
from .const_integration import (
    CONF_BODY_CONTAINS,
    CONF_DOWNLOAD_ATTACHMENTS,
    CONF_ENABLE_AUTOREPLY,
    CONF_FOLDER,
    CONF_HAS_ATTACHMENT,
    CONF_HTML_BODY,
    CONF_IMPORTANCE,
    CONF_IS_UNREAD,
    CONF_MAIL_FROM,
    CONF_MAX_ITEMS,
    CONF_SAVE_ATTACHMENTS,
    CONF_SHOW_BODY,
    CONF_SUBJECT_CONTAINS,
    CONF_SUBJECT_IS,
    Attachment,
    ImportanceLevel,
    Unread,
)

BOOLEAN_SELECTOR = BooleanSelector()


def integration_reconfigure_schema(entry_data):
    """Extend the schame with integration specific attributes."""
    return {
        vol.Optional(
            CONF_ENABLE_UPDATE, default=entry_data[CONF_ENABLE_UPDATE]
        ): cv.boolean,
        vol.Optional(
            CONF_SHARED_MAILBOX,
            description={"suggested_value": entry_data.get(CONF_SHARED_MAILBOX, None)},
        ): cv.string,
        vol.Optional(
            CONF_ENABLE_AUTOREPLY, default=entry_data[CONF_ENABLE_AUTOREPLY]
        ): cv.boolean,
    }


def integration_validate_schema(user_input):  # pylint: disable=unused-argument
    """Validate the user input."""
    return {}


async def async_integration_imports(hass, import_data):  # pylint: disable=unused-argument
    """Do the integration  level import tasks."""
    return


class MS365OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for MS365."""

    def __init__(self, entry: MS365ConfigEntry):
        """Initialize MS365 options flow."""

    async def async_step_init(
        self,
        user_input=None,  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Set up the option flow."""

        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input:
            if user_input.get(CONF_IS_UNREAD) == Unread.NONE:
                del user_input[CONF_IS_UNREAD]
            if user_input.get(CONF_HAS_ATTACHMENT) == Attachment.NONE:
                del user_input[CONF_HAS_ATTACHMENT]
            if user_input.get(CONF_IMPORTANCE) == ImportanceLevel.NONE:
                del user_input[CONF_IMPORTANCE]
            return await self._async_tidy_up(user_input)

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                CONF_ENTITY_NAME: self.config_entry.data[CONF_ENTITY_NAME]
            },
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_FOLDER,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_FOLDER
                            )
                        },
                    ): cv.string,
                    vol.Optional(
                        CONF_MAX_ITEMS,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_MAX_ITEMS, 5
                            )
                        },
                    ): int,
                    vol.Optional(
                        CONF_IS_UNREAD,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_IS_UNREAD, Unread.NONE
                            )
                        },
                    ): vol.In(Unread),
                    vol.Optional(
                        CONF_MAIL_FROM,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_MAIL_FROM
                            )
                        },
                    ): cv.string,
                    vol.Optional(
                        CONF_HAS_ATTACHMENT,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_HAS_ATTACHMENT, Attachment.NONE
                            )
                        },
                    ): vol.In(Attachment),
                    vol.Optional(
                        CONF_IMPORTANCE,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_IMPORTANCE, ImportanceLevel.NONE
                            )
                        },
                    ): vol.In(ImportanceLevel),
                    vol.Exclusive(
                        CONF_SUBJECT_CONTAINS,
                        "subject_contains_or_is",
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_SUBJECT_CONTAINS
                            )
                        },
                    ): cv.string,
                    vol.Exclusive(
                        CONF_SUBJECT_IS,
                        "subject_contains_or_is",
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_SUBJECT_IS
                            )
                        },
                    ): cv.string,
                    vol.Optional(
                        CONF_DOWNLOAD_ATTACHMENTS,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_DOWNLOAD_ATTACHMENTS, True
                            )
                        },
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_SAVE_ATTACHMENTS,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_SAVE_ATTACHMENTS, False
                            )
                        },
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_HTML_BODY,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_HTML_BODY, False
                            )
                        },
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_SHOW_BODY,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_SHOW_BODY, True
                            )
                        },
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_BODY_CONTAINS,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_BODY_CONTAINS
                            )
                        },
                    ): cv.string,
                }
            ),
            errors=errors,
            last_step=True,
        )

    async def _async_tidy_up(self, user_input):
        update = self.async_create_entry(title="", data=user_input)
        await self.hass.config_entries.async_reload(self._config_entry_id)
        return update
