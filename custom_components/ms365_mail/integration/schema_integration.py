"""Schema for MS365 Integration."""

import probatio

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_MESSAGE,
    ATTR_TARGET,
    ATTR_TITLE,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import BooleanSelector
from O365.mailbox import ExternalAudience  # pylint: disable=no-name-in-module, import-error
from O365.utils import ImportanceLevel as O365IL  # pylint: disable=no-name-in-module

from ..const import CONF_ENABLE_UPDATE, CONF_ENTITY_NAME, CONF_SHARED_MAILBOX
from .const_integration import (
    ATTR_ATTACHMENTS,
    ATTR_END,
    ATTR_EXTERNAL_AUDIENCE,
    ATTR_EXTERNALREPLY,
    ATTR_FROM,
    ATTR_IMPORTANCE,
    ATTR_INTERNALREPLY,
    ATTR_MESSAGE_IS_HTML,
    ATTR_PHOTOS,
    ATTR_SENDER,
    ATTR_START,
    ATTR_SUBJECT,
    ATTR_TO,
    ATTR_ZIP_ATTACHMENTS,
    ATTR_ZIP_NAME,
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

CONFIG_SCHEMA_INTEGRATION = {
    probatio.Optional(CONF_ENABLE_UPDATE, default=False): cv.boolean,
    probatio.Optional(CONF_SHARED_MAILBOX, default=""): cv.string,
    probatio.Optional(CONF_ENABLE_AUTOREPLY, default=False): cv.boolean,
}

MAIL_FOLDER_SCHEMA = {
    probatio.Required(CONF_ENTITY_NAME): cv.string,
    probatio.Optional(CONF_FOLDER): cv.string,
    probatio.Optional(CONF_MAX_ITEMS): int,
    probatio.Optional(CONF_IS_UNREAD): probatio.In(Unread),
    probatio.Optional(CONF_MAIL_FROM): cv.string,
    probatio.Optional(CONF_HAS_ATTACHMENT): probatio.In(Attachment),
    probatio.Optional(CONF_IMPORTANCE): probatio.In(ImportanceLevel),
    probatio.Exclusive(CONF_SUBJECT_CONTAINS, "subject_contains_or_is"): cv.string,
    probatio.Exclusive(CONF_SUBJECT_IS, "subject_contains_or_is"): cv.string,
    probatio.Optional(CONF_DOWNLOAD_ATTACHMENTS): BooleanSelector(),
    probatio.Optional(CONF_SAVE_ATTACHMENTS): BooleanSelector(),
    probatio.Optional(CONF_HTML_BODY): BooleanSelector(),
    probatio.Optional(CONF_SHOW_BODY): BooleanSelector(),
    probatio.Optional(CONF_BODY_CONTAINS): cv.string,
}


NOTIFY_SERVICE_DATA_SCHEMA = probatio.Schema(
    {
        probatio.Optional(ATTR_MESSAGE_IS_HTML, default=False): bool,
        probatio.Optional(ATTR_TARGET): probatio.Any(cv.string, [cv.string]),
        probatio.Optional(ATTR_SENDER): cv.string,
        probatio.Optional(ATTR_ZIP_ATTACHMENTS, default=False): bool,
        probatio.Optional(ATTR_ZIP_NAME): cv.string,
        probatio.Optional(ATTR_PHOTOS, default=[]): [cv.string],
        probatio.Optional(ATTR_ATTACHMENTS, default=[]): [cv.string],
        probatio.Optional(ATTR_IMPORTANCE): probatio.Coerce(O365IL),
    }
)

NOTIFY_SERVICE_BASE_SCHEMA = probatio.Schema(
    {
        probatio.Optional(ATTR_TARGET, default=[]): [cv.string],
        probatio.Optional(ATTR_TITLE, default=""): cv.string,
        probatio.Optional(ATTR_DATA): NOTIFY_SERVICE_DATA_SCHEMA,
    }
)

AUTO_REPLY_SERVICE_ENABLE_SCHEMA = {
    probatio.Required(ATTR_EXTERNALREPLY): cv.string,
    probatio.Required(ATTR_INTERNALREPLY): cv.string,
    probatio.Optional(ATTR_START): cv.datetime,
    probatio.Optional(ATTR_END): cv.datetime,
    probatio.Optional(ATTR_EXTERNAL_AUDIENCE): probatio.Coerce(ExternalAudience),
}

AUTO_REPLY_SERVICE_DISABLE_SCHEMA = {}

MAIL_SEND_SCHEMA = {
    probatio.Required(ATTR_SUBJECT): cv.string,
    probatio.Required(ATTR_MESSAGE): cv.string,
    probatio.Optional(ATTR_TO): probatio.All(cv.ensure_list, [cv.string]),
    probatio.Optional(ATTR_MESSAGE_IS_HTML, default=False): bool,
    probatio.Optional(ATTR_FROM): cv.string,
    probatio.Optional(ATTR_ZIP_ATTACHMENTS, default=False): bool,
    probatio.Optional(ATTR_ZIP_NAME): cv.string,
    probatio.Optional(ATTR_PHOTOS, default=[]): [cv.string],
    probatio.Optional(ATTR_ATTACHMENTS, default=[]): [cv.string],
    probatio.Optional(ATTR_IMPORTANCE): probatio.Coerce(O365IL),
}
