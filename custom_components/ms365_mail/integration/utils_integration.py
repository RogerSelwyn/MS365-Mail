"""Mail utilities processes."""

import os
import warnings
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

from ..const import DATETIME_FORMAT
from .const_integration import (
    ATTR_ATTACHMENTS,
    ATTR_MESSAGE_IS_HTML,
    ATTR_PHOTOS,
    ATTR_ZIP_ATTACHMENTS,
    ATTR_ZIP_NAME,
)

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def clean_html(html):
    """Clean the HTML."""
    soup = BeautifulSoup(html, features="html.parser")
    if body := soup.find("body"):
        # get text
        text = body.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text.replace("\xa0", " ")

    return html


def get_email_attributes(mail, download_attachments, html_body, show_body):
    """Get the email attributes."""
    data = {
        "subject": mail.subject,
        "received": mail.received.strftime(DATETIME_FORMAT),
        "to": [x.address for x in mail.to],
        "cc": [x.address for x in mail.cc],
        "sender": mail.sender.address,
        "has_attachments": mail.has_attachments,
        "importance": mail.importance.value,
        "is_read": mail.is_read,
        "flag": {
            "is_flagged": mail.flag.is_flagged,
            "is_completed": mail.flag.is_completed,
            "due_date": mail.flag.due_date,
            "completion_date": mail.flag.completition_date,
        },
    }

    if show_body or html_body:
        data["body"] = _safe_html(mail.body) if html_body else clean_html(mail.body)
    if download_attachments:
        data["attachments"] = [x.name for x in mail.attachments]

    return data


def _safe_html(html):
    """Make the HTML safe."""
    soup = BeautifulSoup(html, features="html.parser")
    if soup.find("body"):
        blacklist = ["script", "style"]
        for tag in soup.find_all():
            if tag.name.lower() in blacklist:
                # blacklisted tags are removed in their entirety
                tag.extract()
        return str(soup.find("body"))
    return html


def build_message(hass, data, message, new_message_attachments):
    """Build a message to send"""
    is_html = False
    photos = []
    if data:
        is_html = data.get(ATTR_MESSAGE_IS_HTML, False)
        photos = data.get(ATTR_PHOTOS, [])
    if is_html or photos:
        message = f"""
            <html>
                <body>
                    {message}"""
        message += _build_photo_content(hass, photos, new_message_attachments)
        message += "</body></html>"

    return message


def _build_photo_content(hass, photos, new_message_attachments):
    photos_content = ""
    for i, photo in enumerate(photos, start=1):
        if photo.startswith("http"):
            photos_content += f'<br><img src="{photo}">'
        else:
            photo = _get_ha_filepath(hass, photo)
            new_message_attachments.add(photo)
            att = new_message_attachments[-1]
            att.is_inline = True
            att.content_id = str(i)
            photos_content += f'<br><img src="cid:{att.content_id}">'

    return photos_content


def build_attachments(hass, data, new_message_attachments):
    """Build the attachments"""
    attachments = []
    zip_attachments = False
    zip_name = None
    cleanup_files = []
    if data:
        attachments = data.get(ATTR_ATTACHMENTS, [])
        zip_attachments = data.get(ATTR_ZIP_ATTACHMENTS, False)
        zip_name = data.get(ATTR_ZIP_NAME, None)

    attachments = [_get_ha_filepath(hass, x) for x in attachments]
    if attachments and zip_attachments:
        z_file = _zip_files(attachments, zip_name)
        new_message_attachments.add(z_file)
        cleanup_files.append(z_file)

    else:
        for attachment in attachments:
            new_message_attachments.add(attachment)
    return cleanup_files


def cleanup(cleanup_files):
    """Cleanup any files."""
    for filename in cleanup_files:
        os.remove(filename)


def _get_ha_filepath(hass, filepath):
    """Get the file path."""
    _filepath = Path(filepath)
    if _filepath.parts[0] == "/" and _filepath.parts[1] == "config":
        _filepath = os.path.join(hass.config.config_dir, *_filepath.parts[2:])

    if not os.path.isfile(_filepath):
        if not os.path.isfile(filepath):
            raise ValueError(f"Could not access file {filepath} at {_filepath}")
        return filepath  # pragma: no cover
    return _filepath


def _zip_files(filespaths, zip_name):
    """Zip the files."""
    if not zip_name:
        zip_name = "archive.zip"
    if Path(zip_name).suffix != ".zip":
        zip_name += ".zip"

    with zipfile.ZipFile(zip_name, mode="w") as zip_file:
        for file_path in filespaths:
            zip_file.write(file_path, os.path.basename(file_path))
    return zip_name
