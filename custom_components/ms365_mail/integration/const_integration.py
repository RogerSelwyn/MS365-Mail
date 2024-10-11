"""Mail constants."""

from enum import StrEnum

from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.SENSOR]
DOMAIN = "ms365_mail"
ATTACHMENT_FOLDER = "attachments"

ATTR_AUTOREPLIESSETTINGS = "autorepliessettings"
ATTR_ATTACHMENTS = "attachments"
ATTR_END = "end"
ATTR_EXTERNAL_AUDIENCE = "external_audience"
ATTR_EXTERNALREPLY = "external_reply"
ATTR_IMPORTANCE = "importance"
ATTR_INTERNALREPLY = "internal_reply"
ATTR_MESSAGE_IS_HTML = "message_is_html"
ATTR_PHOTOS = "photos"
ATTR_SENDER = "sender"
ATTR_START = "start"
ATTR_STATE = "state"
ATTR_ZIP_ATTACHMENTS = "zip_attachments"
ATTR_ZIP_NAME = "zip_name"

CONF_BODY_CONTAINS = "body_contains"
CONF_DOWNLOAD_ATTACHMENTS = "download_attachments"
CONF_ENABLE_AUTOREPLY = "enable_autoreply"
CONF_ENTRY = "entry"
CONF_FOLDER = "folder"
CONF_IMPORTANCE = "importance"
CONF_IS_UNREAD = "is_unread"
CONF_HAS_ATTACHMENT = "has_attachment"
CONF_HTML_BODY = "html_body"
CONF_MAIL_FROM = "from"
CONF_MAX_ITEMS = "max_items"
CONF_MS365_MAIL_FOLDER = "mail_folder"
CONF_QUERY = "query"
CONF_SAVE_ATTACHMENTS = "save_attachments"
CONF_SHOW_BODY = "show_body"
CONF_SUBJECT_CONTAINS = "subject_contains"
CONF_SUBJECT_IS = "subject_is"

ENTITY_ID_FORMAT_SENSOR = "sensor.{}"

PERM_MAILBOX_SETTINGS = "MailboxSettings.ReadWrite"
PERM_MAIL_READ = "Mail.Read"
PERM_MAIL_SEND = "Mail.Send"

SENSOR_EMAIL = "inbox"
SENSOR_AUTO_REPLY = "auto_reply"


class Unread(StrEnum):
    """Mail Unread."""

    TRUE = "Unread Only"
    FALSE = "Read Only"
    NONE = "All"


class Attachment(StrEnum):
    """Mail Attachment."""

    TRUE = "Has attachment"
    FALSE = "Does not have attachment"
    NONE = "All"


class ImportanceLevel(StrEnum):
    """Mail Importance Level."""

    NORMAL = "Normal"
    LOW = "Low"
    HIGH = "High"
    NONE = "All"
