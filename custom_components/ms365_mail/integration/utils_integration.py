"""Mail utilities processes."""

from bs4 import BeautifulSoup

from ..const import DATETIME_FORMAT
from ..helpers.utils import clean_html


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
