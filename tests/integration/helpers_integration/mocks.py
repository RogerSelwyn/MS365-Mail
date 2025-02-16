"""Mock setup."""

# from datetime import timedelta

from ...helpers.utils import mock_call  # utcnow
from ..const_integration import URL


class MS365Mocks:
    """Standard mocks."""

    def standard_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, URL.OPENID, "openid")
        mock_call(requests_mock, URL.ME, "me")
        mock_call(requests_mock, URL.INBOX, "inbox_messages")
        mock_call(requests_mock, URL.AUTOREPLY, "autoreply")
        mock_call(requests_mock, URL.ATTACHMENT, "attachment")
        mock_call(requests_mock, URL.SHARED_INBOX, "shared_inbox_messages")


MS365MOCKS = MS365Mocks()
