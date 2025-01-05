"""Generic Permissions processes."""

import json
import logging
import os
from copy import deepcopy

from O365 import Account, FileSystemTokenBackend

from ..const import (
    CONF_ENTITY_NAME,
    CONST_UTC_TIMEZONE,
    MS365_STORAGE_TOKEN,
    PERM_OFFLINE_ACCESS,
    TOKEN_FILE_CORRUPTED,
    TOKEN_FILE_MISSING,
    TOKEN_FILE_PERMISSIONS,
    TOKEN_FILENAME,
)
from ..helpers.filemgmt import build_config_file_path
from ..integration.const_integration import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BasePermissions:
    """Class in support of building permission sets."""

    def __init__(self, hass, config):
        """Initialise the class."""
        self._hass = hass
        self._config = config

        self._requested_permissions = []
        self._permissions = []
        self.token_filename = self.build_token_filename()
        self.token_path = build_config_file_path(self._hass, MS365_STORAGE_TOKEN)
        _LOGGER.debug("Setup token")
        self.token_backend = FileSystemTokenBackend(
            token_path=self.token_path,
            token_filename=self.token_filename,
        )

    @property
    def requested_permissions(self):
        """Return the required scope."""

    @property
    def permissions(self):
        """Return the permission set."""
        return self._permissions

    def try_authentication(self, credentials, main_resource):
        """Try authenticating to O365."""
        _LOGGER.debug("Setup account")
        account = Account(
            credentials,
            token_backend=self.token_backend,
            timezone=CONST_UTC_TIMEZONE,
            main_resource=main_resource,
        )
        try:
            return account, account.is_authenticated, False

        except json.decoder.JSONDecodeError as err:
            _LOGGER.error("Error authenticating - JSONDecodeError - %s", err)
            return account, False, err

    async def async_check_authorizations(self):
        """Report on permissions status."""
        self._permissions = await self._hass.async_add_executor_job(
            self._get_permissions
        )

        if self._permissions in [TOKEN_FILE_CORRUPTED, TOKEN_FILE_MISSING]:
            return self._permissions, None
        failed_permissions = []
        for permission in self.requested_permissions:
            if permission == PERM_OFFLINE_ACCESS:
                continue
            if not self.validate_authorization(permission):
                failed_permissions.append(permission)

        if failed_permissions:
            _LOGGER.warning(
                "Minimum required permissions: '%s'. Not available in token '%s' for account '%s'.",
                ", ".join(failed_permissions),
                self.token_filename,
                self._config[CONF_ENTITY_NAME],
            )
            return TOKEN_FILE_PERMISSIONS, failed_permissions

        return True, None

    def validate_authorization(self, permission):
        """Validate higher permissions."""
        if permission in self.permissions:
            return True

        if self._check_higher_permissions(permission):
            return True

        resource = permission.split(".")[0]
        constraint = (
            permission.split(".")[2] if len(permission.split(".")) == 3 else None
        )

        # If Calendar or Mail Resource then permissions can have a constraint of .Shared
        # which includes base as well. e.g. Calendars.Read is also enabled by Calendars.Read.Shared
        if not constraint and resource in ["Calendars", "Mail"]:
            sharedpermission = f"{deepcopy(permission)}.Shared"
            return self._check_higher_permissions(sharedpermission)
        # If Presence Resource then permissions can have a constraint of .All
        # which includes base as well. e.g. Presencedar.Read is also enabled by Presence.Read.All
        if not constraint and resource in ["Presence"]:
            allpermission = f"{deepcopy(permission)}.All"
            return self._check_higher_permissions(allpermission)

        return False

    def _check_higher_permissions(self, permission):
        operation = permission.split(".")[1]
        # If Operation is Send there are no alternatives
        # If Operation is ReadBasic then Read or ReadWrite will also work
        # If Operation is Read then ReadWrite will also work
        if operation == "Send":
            newops = ["Send"]
        elif operation == "ReadBasic":
            newops = ["ReadBasic", "Read", "ReadWrite"]
        elif operation == "Read":
            newops = ["Read", "ReadWrite"]
        else:
            newops = []
        for newop in newops:
            newperm = deepcopy(permission).replace(operation, newop)
            if newperm in self.permissions:
                return True

        return False

    def build_token_filename(self):
        """Create the token file name."""
        return TOKEN_FILENAME.format(DOMAIN, f"_{self._config.get(CONF_ENTITY_NAME)}")

    def _get_permissions(self):
        """Get the permissions from the token file."""
        full_token_path = os.path.join(self.token_path, self.token_filename)
        if not os.path.exists(full_token_path) or not os.path.isfile(full_token_path):
            _LOGGER.warning("Could not locate token at %s", full_token_path)
            return TOKEN_FILE_MISSING
        try:
            with open(full_token_path, "r", encoding="UTF-8") as file_handle:
                raw = file_handle.read()
                permissions = json.loads(raw)["scope"]
        except json.decoder.JSONDecodeError as err:
            _LOGGER.warning(
                (
                    "Token corrupted for integration %s, unique identifier %s, "
                    + "please re-configure and re-authenticate - %s"
                ),
                DOMAIN,
                self._config[CONF_ENTITY_NAME],
                err,
            )
            return TOKEN_FILE_CORRUPTED

        return permissions

    def delete_token(self):
        """Delete the token."""
        full_token_path = os.path.join(self.token_path, self.token_filename)
        if os.path.exists(full_token_path):
            os.remove(full_token_path)
