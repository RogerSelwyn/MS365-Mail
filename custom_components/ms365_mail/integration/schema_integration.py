"""Schema for MS365 Integration."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
)
from O365.mailbox import (  # pylint: disable=no-name-in-module, import-error
    ExternalAudience,
)
from O365.utils import ImportanceLevel  # pylint: disable=no-name-in-module

from ..const import CONF_ENABLE_UPDATE, CONF_SHARED_MAILBOX
from .const_integration import (
    ATTR_ATTACHMENTS,
    ATTR_END,
    ATTR_EXTERNAL_AUDIENCE,
    ATTR_EXTERNALREPLY,
    ATTR_IMPORTANCE,
    ATTR_INTERNALREPLY,
    ATTR_MESSAGE_IS_HTML,
    ATTR_PHOTOS,
    ATTR_SENDER,
    ATTR_START,
    ATTR_ZIP_ATTACHMENTS,
    ATTR_ZIP_NAME,
    CONF_ENABLE_AUTOREPLY,
)

CONFIG_SCHEMA_INTEGRATION = {
    vol.Optional(CONF_ENABLE_UPDATE, default=False): cv.boolean,
    vol.Optional(CONF_SHARED_MAILBOX, default=""): cv.string,
    vol.Optional(CONF_ENABLE_AUTOREPLY, default=""): cv.boolean,
}

NOTIFY_SERVICE_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_MESSAGE_IS_HTML, default=False): bool,
        vol.Optional(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_SENDER): cv.string,
        vol.Optional(ATTR_ZIP_ATTACHMENTS, default=False): bool,
        vol.Optional(ATTR_ZIP_NAME): cv.string,
        vol.Optional(ATTR_PHOTOS, default=[]): [cv.string],
        vol.Optional(ATTR_ATTACHMENTS, default=[]): [cv.string],
        vol.Optional(ATTR_IMPORTANCE): vol.Coerce(ImportanceLevel),
    }
)

NOTIFY_SERVICE_BASE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_TARGET, default=[]): [cv.string],
        vol.Optional(ATTR_TITLE, default=""): cv.string,
        vol.Optional(ATTR_DATA): NOTIFY_SERVICE_DATA_SCHEMA,
    }
)

AUTO_REPLY_SERVICE_ENABLE_SCHEMA = {
    vol.Required(ATTR_EXTERNALREPLY): cv.string,
    vol.Required(ATTR_INTERNALREPLY): cv.string,
    vol.Optional(ATTR_START): cv.datetime,
    vol.Optional(ATTR_END): cv.datetime,
    vol.Optional(ATTR_EXTERNAL_AUDIENCE): vol.Coerce(ExternalAudience),
}

AUTO_REPLY_SERVICE_DISABLE_SCHEMA = {}
