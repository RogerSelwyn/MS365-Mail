# pylint: disable=unused-import,line-too-long
"""Constants for mail integration."""

from copy import deepcopy
from enum import Enum

from custom_components.ms365_mail.config_flow import MS365ConfigFlow  # noqa: F401
from custom_components.ms365_mail.const import (  # noqa: F401
    AUTH_CALLBACK_PATH_ALT,
    AUTH_CALLBACK_PATH_DEFAULT,
)
from custom_components.ms365_mail.integration.const_integration import (
    DOMAIN,  # noqa: F401
)

from ..const import CLIENT_ID, CLIENT_SECRET, ENTITY_NAME

BASE_CONFIG_ENTRY = {
    "entity_name": ENTITY_NAME,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "alt_auth_method": False,
    "enable_update": False,
    "enable_autoreply": False,
    "shared_mailbox": "",
}
BASE_TOKEN_PERMS = "Mail.Read"
BASE_MISSING_PERMS = BASE_TOKEN_PERMS
SHARED_TOKEN_PERMS = "Mail.Read.Shared"
UPDATE_TOKEN_PERMS = "Mail.Read Mail.Send MailboxSettings.ReadWrite"
UPDATE_OPTIONS = {"enable_update": True}

ALT_CONFIG_ENTRY = deepcopy(BASE_CONFIG_ENTRY)
ALT_CONFIG_ENTRY["alt_auth_method"] = True

RECONFIGURE_CONFIG_ENTRY = deepcopy(BASE_CONFIG_ENTRY)
del RECONFIGURE_CONFIG_ENTRY["entity_name"]

MIGRATION_CONFIG_ENTRY = {
    "data": BASE_CONFIG_ENTRY,
    "options": {},
}

DIAGNOSTIC_GRANTED_PERMISSIONS = [
    "Mail.Read",
    "User.Read",
    "email",
    "openid",
    "profile",
]
DIAGNOSTIC_REQUESTED_PERMISSIONS = [
    "User.Read",
    "Mail.Read",
]

FULL_INIT_ENTITY_NO = 1


class URL(Enum):
    """List of URLs"""

    OPENID = (
        "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
    )
    ME = "https://graph.microsoft.com/v1.0/me"
    INBOX = "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"
    AUTOREPLY = "https://graph.microsoft.com/v1.0/me/mailboxSettings"
    ATTACHMENT = "https://graph.microsoft.com/v1.0/me/messages/mail1/attachments"
    ROOTFOLDER = "https://graph.microsoft.com/v1.0/me/mailFolders"
    CHILDFOLDER = "https://graph.microsoft.com/v1.0/me/mailFolders/rootfolderid/childFolders?%24filter=displayName+eq+%27SubFolder%27&%24top=1"
    CHILDMESSAGES = (
        "https://graph.microsoft.com/v1.0/me/mailFolders/childfolderid/messages"
    )
    BADFOLDER = "https://graph.microsoft.com/v1.0/me/mailFolders/rootfolderid/childFolders?%24filter=displayName+eq+%27BadFolder%27&%24top=1"
    SHARED_INBOX = "https://graph.microsoft.com/v1.0/users/jane.doe@nomail.com/mailFolders/Inbox/messages"
