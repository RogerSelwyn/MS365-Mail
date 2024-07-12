"""Configuration flow for the skyq platform."""

import functools as ft
import json
import logging
from collections.abc import Mapping
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from aiohttp import web_response
from homeassistant import (
    config_entries,  # exceptions
    data_entry_flow,
)
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
from homeassistant.helpers.network import get_url
from O365 import Account, FileSystemTokenBackend

from .const import (
    AUTH_CALLBACK_NAME,
    AUTH_CALLBACK_PATH_ALT,
    AUTH_CALLBACK_PATH_DEFAULT,
    CONF_ALT_AUTH_METHOD,
    CONF_AUTH_URL,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_ENTITY_NAME,
    CONF_FAILED_PERMISSIONS,
    CONF_SHARED_MAILBOX,
    CONF_URL,
    CONST_UTC_TIMEZONE,
    TOKEN_FILE_MISSING,
)
from .helpers.config_entry import MS365ConfigEntry
from .integration.config_flow_integration import (
    MS365OptionsFlowHandler,
    integration_reconfigure_schema,
    integration_validate_schema,
)
from .integration.const_integration import DOMAIN
from .integration.permissions_integration import Permissions
from .integration.schema_integration import CONFIG_SCHEMA_INTEGRATION
from .schema import (
    CONFIG_SCHEMA,
    REQUEST_AUTHORIZATION_DEFAULT_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


class MS365ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initiliase the configuration flow."""
        self._permissions = []
        self._failed_permissions = []
        self._account = None
        self._entity_name = None
        self._url = None
        self._callback_url = None
        self._state = None
        self._callback_view = None
        self._alt_auth_method = None
        self._user_input = None
        self._config_schema: dict[vol.Required, type[str | int]] | None = None
        self._reconfigure = False
        self._entry: MS365ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """MS365 options callback."""
        return MS365OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input:
            errors = integration_validate_schema(user_input)
        if user_input and not errors:
            self._user_input = user_input

            if not self._entity_name:
                self._entity_name = user_input.get(CONF_ENTITY_NAME)
            else:
                user_input[CONF_ENTITY_NAME] = self._entity_name
            credentials = (
                user_input.get(CONF_CLIENT_ID),
                user_input.get(CONF_CLIENT_SECRET),
            )

            main_resource = user_input.get(CONF_SHARED_MAILBOX)
            self._alt_auth_method = user_input.get(CONF_ALT_AUTH_METHOD)
            self._permissions = Permissions(self.hass, user_input)
            self._permissions.token_filename = self._permissions.build_token_filename()
            self._account, is_authenticated = await self._async_try_authentication(
                self._permissions, credentials, main_resource, self._entity_name
            )
            if not is_authenticated or self._reconfigure:
                scope = self._permissions.requested_permissions
                self._callback_url = get_callback_url(self.hass, self._alt_auth_method)
                self._url, self._state = self._account.con.get_authorization_url(
                    requested_scopes=scope, redirect_uri=self._callback_url
                )

                if self._alt_auth_method:
                    return await self.async_step_request_alt()

                return await self.async_step_request_default()

            errors[CONF_ENTITY_NAME] = "already_configured"

        data = self._config_schema or CONFIG_SCHEMA | CONFIG_SCHEMA_INTEGRATION
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data), errors=errors
        )

    async def async_step_request_default(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the confirm step of a fix flow."""
        errors = {}
        _LOGGER.debug("Token file: %s", self._account.con.token_backend)
        if user_input is not None:
            errors = await self._async_validate_response(user_input)
            if not errors:
                return await self._async_create_update_entry()

        failed_permissions = None
        if self._failed_permissions:
            failed_permissions = f"\n\n {', '.join(self._failed_permissions)}"
        return self.async_show_form(
            step_id="request_default",
            data_schema=vol.Schema(REQUEST_AUTHORIZATION_DEFAULT_SCHEMA),
            description_placeholders={
                CONF_AUTH_URL: self._url,
                CONF_ENTITY_NAME: self._entity_name,
                CONF_FAILED_PERMISSIONS: failed_permissions,
            },
            errors=errors,
        )

    async def async_step_request_alt(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the confirm step of a fix flow."""
        errors = {}
        if user_input is not None:
            errors = await self._async_validate_response(user_input)
            if not errors:
                return await self._async_create_update_entry()

        if not self._callback_view:
            self._callback_view = MS365AuthCallbackView()
            self.hass.http.register_view(self._callback_view)

        failed_permissions = None
        if self._failed_permissions:
            failed_permissions = f"\n\nMissing - {', '.join(self._failed_permissions)}"

        return self.async_show_form(
            step_id="request_alt",
            description_placeholders={
                CONF_AUTH_URL: self._url,
                CONF_ENTITY_NAME: self._entity_name,
                CONF_FAILED_PERMISSIONS: failed_permissions,
            },
            errors=errors,
        )

    async def _async_create_update_entry(self):
        if self._reconfigure:
            self.hass.config_entries.async_update_entry(
                self._entry,
                data=self._user_input,
            )
            await self.hass.config_entries.async_reload(self._entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_create_entry(title=self._entity_name, data=self._user_input)

    async def _async_validate_response(self, user_input):
        errors = {}
        url = (
            self._callback_view.token_url
            if self._alt_auth_method
            else user_input[CONF_URL]
        )
        if url[:5].lower() == "http:":
            url = f"https:{url[5:]}"
        if "code" not in url:
            errors[CONF_URL] = "invalid_url"
            return errors

        result = await self.hass.async_add_executor_job(
            ft.partial(
                self._account.con.request_token,
                url,
                state=self._state,
                redirect_uri=self._callback_url,
            )
        )

        if result is not True:
            _LOGGER.error("Token file error - check log for errors from O365")
            errors[CONF_URL] = "token_file_error"
            return errors

        (
            permissions,
            self._failed_permissions,
        ) = await self._permissions.async_check_authorizations()
        if permissions == TOKEN_FILE_MISSING:
            errors[CONF_URL] = "missing_token_file"
            return errors

        if not permissions:
            errors[CONF_URL] = "minimum_permissions"

        return errors

    async def _async_try_authentication(
        self, perms, credentials, main_resource, entity_name
    ):
        _LOGGER.debug("Setup token")
        token_backend = await self.hass.async_add_executor_job(
            ft.partial(
                FileSystemTokenBackend,
                token_path=perms.token_path,
                token_filename=perms.token_filename,
            )
        )
        _LOGGER.debug("Setup account")
        account = await self.hass.async_add_executor_job(
            ft.partial(
                Account,
                credentials,
                token_backend=token_backend,
                timezone=CONST_UTC_TIMEZONE,
                main_resource=main_resource,
            )
        )
        try:
            return account, account.is_authenticated

        except json.decoder.JSONDecodeError as err:
            _LOGGER.warning(
                "Token corrupt for account - please delete and re-authenticate: %s. Error - %s",
                entity_name,
                err,
            )
            return account, False

    async def async_step_reconfigure(
        self,
        user_input: Mapping[str, Any] | None = None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Trigger a reconfiguration flow."""
        self._entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        assert self._entry
        return await self._redo_configuration(self._entry.data)

    async def _redo_configuration(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Re-run configuration step."""

        self._reconfigure = True
        self._entity_name = entry_data[CONF_ENTITY_NAME]
        self._config_schema = {
            vol.Required(CONF_CLIENT_ID, default=entry_data[CONF_CLIENT_ID]): vol.All(
                cv.string, vol.Strip
            ),
            vol.Required(
                CONF_CLIENT_SECRET, default=entry_data[CONF_CLIENT_SECRET]
            ): vol.All(cv.string, vol.Strip),
            vol.Optional(
                CONF_ALT_AUTH_METHOD, default=entry_data[CONF_ALT_AUTH_METHOD]
            ): cv.boolean,
        }
        self._config_schema = self._config_schema | integration_reconfigure_schema(
            entry_data
        )

        return await self.async_step_user()


def get_callback_url(hass, alt_config):
    """Get the callback URL."""
    if alt_config:
        return f"{get_url(hass, prefer_external=True)}{AUTH_CALLBACK_PATH_ALT}"

    return AUTH_CALLBACK_PATH_DEFAULT


class MS365AuthCallbackView(HomeAssistantView):
    """MS365 Authorization Callback View."""

    requires_auth = False
    url = AUTH_CALLBACK_PATH_ALT
    name = AUTH_CALLBACK_NAME

    def __init__(self):
        """Initialize."""
        self.token_url = None

    @callback
    async def get(self, request):
        """Receive authorization token."""
        self.token_url = str(request.url)

        return web_response.Response(
            headers={"content-type": "text/html"},
            text="<script>window.close()</script>This window can be closed",
        )
