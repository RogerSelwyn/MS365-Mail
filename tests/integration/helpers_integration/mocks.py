"""Mock setup."""

# from datetime import timedelta

from ...helpers.utils import mock_call, load_json
from ..const_integration import CN21VURL, URL


class MS365Mocks:
    """Standard mocks."""

    def cn21v_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, CN21VURL.DISCOVERY, "discovery")
        # Mock the /common/ openid config with CN21V-specific URLs.
        # MSAL fetches this via the discovery response's tenant_discovery_endpoint.
        openid_data = load_json("O365/openid.json")
        openid_data = openid_data.replace(
            "login.microsoftonline.com",
            "login.partner.microsoftonline.cn",
        )
        requests_mock.get(CN21VURL.OPENID.value, text=openid_data)
        mock_call(requests_mock, CN21VURL.ME, "me")
        mock_call(requests_mock, CN21VURL.INBOX, "inbox_messages")

    def standard_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, URL.OPENID, "openid")
        mock_call(requests_mock, URL.ME, "me")
        mock_call(requests_mock, URL.INBOX, "inbox_messages")
        mock_call(requests_mock, URL.AUTOREPLY, "autoreply")
        mock_call(requests_mock, URL.ATTACHMENT, "attachment")
        mock_call(requests_mock, URL.SHARED_INBOX, "shared_inbox_messages")


MS365MOCKS = MS365Mocks()
