# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test service usage."""

import shutil
from unittest.mock import patch

import pytest
from homeassistant.components.notify import DOMAIN as NOTIFY_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from custom_components.ms365_mail.const import CONF_ENABLE_UPDATE
from custom_components.ms365_mail.integration.const_integration import (
    CONF_ENABLE_AUTOREPLY,
)

from ..conftest import MS365MockConfigEntry
from ..const import TEST_DATA_INTEGRATION_LOCATION
from .const_integration import DOMAIN


async def test_update_service_setup(
    hass: HomeAssistant,
    setup_update_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the reconfigure flow."""
    assert base_config_entry.data[CONF_ENABLE_UPDATE]
    assert not hass.services.has_service(DOMAIN, "auto_reply_enable")
    assert not hass.services.has_service(DOMAIN, "auto_reply_disable")
    assert hass.services.has_service(NOTIFY_DOMAIN, "ms365_mail_test")


@pytest.mark.parametrize(
    "base_config_entry",
    [{"enable_autoreply": True, "enable_update": True}],
    indirect=True,
)
@pytest.mark.parametrize(
    "base_token", ["Mail.Read Mail.Send MailboxSettings.ReadWrite"], indirect=True
)
async def test_autoreply_service_setup(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the reconfigure flow."""
    assert base_config_entry.data[CONF_ENABLE_AUTOREPLY]
    assert hass.services.has_service(DOMAIN, "auto_reply_enable")
    assert hass.services.has_service(DOMAIN, "auto_reply_disable")


@pytest.mark.parametrize(
    "base_config_entry",
    [{"enable_autoreply": True, "enable_update": True}],
    indirect=True,
)
@pytest.mark.parametrize(
    "base_token", ["Mail.Read Mail.Send MailboxSettings.ReadWrite"], indirect=True
)
async def test_autoreply(
    hass: HomeAssistant,
    setup_base_integration,
) -> None:
    """Test autoreply."""
    entity_name = "sensor.test_autoreply"
    with patch("O365.mailbox.MailBox.set_automatic_reply") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "auto_reply_enable",
            {
                "entity_id": entity_name,
                "external_reply": "External Message",
                "internal_reply": "Internal Message",
                "start": "2025-01-01T12:00:00+0000",
                "end": "2025-01-01T12:30:00+0000",
                "external_audience": "all",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called

    with patch("O365.mailbox.MailBox.set_disable_reply") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "auto_reply_disable",
            {
                "entity_id": entity_name,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called


@pytest.mark.parametrize(
    "base_config_entry",
    [{"enable_autoreply": True, "enable_update": True}],
    indirect=True,
)
@pytest.mark.parametrize(
    "base_token", ["Mail.Read Mail.Send MailboxSettings.ReadWrite"], indirect=True
)
async def test_autoreply_failed_permission(
    hass: HomeAssistant,
    setup_base_integration,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test notify - HA Service."""
    entity_name = "sensor.test_autoreply"
    failed_perm = "mail.failed_perm"
    with (
        patch(
            f"custom_components.{DOMAIN}.integration.sensor_integration.PERM_MAILBOX_SETTINGS",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            DOMAIN,
            "auto_reply_enable",
            {
                "entity_id": entity_name,
                "external_reply": "External Message",
                "internal_reply": "Internal Message",
                "start": "2025-01-01T12:00:00+0000",
                "end": "2025-01-01T12:30:00+0000",
                "external_audience": "all",
            },
            blocking=True,
            return_response=False,
        )
    assert (
        f"Not authorised to update auto reply - requires permission: {failed_perm}"
        in str(exc_info.value)
    )
    with (
        patch(
            f"custom_components.{DOMAIN}.integration.sensor_integration.PERM_MAILBOX_SETTINGS",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            DOMAIN,
            "auto_reply_disable",
            {
                "entity_id": entity_name,
            },
            blocking=True,
            return_response=False,
        )
    assert (
        f"Not authorised to update auto reply - requires permission: {failed_perm}"
        in str(exc_info.value)
    )


async def test_notify(
    hass: HomeAssistant,
    setup_update_integration,
) -> None:
    """Test notify - HA Service."""
    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called

    assert "'toRecipients': [{'emailAddress': {'address': 'john@nomail.com'}}]" in str(
        mock_new_message.mock_calls
    )

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "sender": "sender@nomail.com",
                    "importance": "normal",
                    "message_is_html": True,
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert "'from': {'emailAddress': {'address': 'sender@nomail.com'}}" in str(
        mock_new_message.mock_calls
    )

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {"target": "target@nomail.com"},
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert (
        "'toRecipients': [{'emailAddress': {'address': 'target@nomail.com'}}]"
        in str(mock_new_message.mock_calls)
    )


async def test_attachments(
    adjust_config_dir,
    hass: HomeAssistant,
    setup_update_integration,
    tmp_path,
) -> None:
    """Test notify - HA Service."""
    filepath = attachment_setup(tmp_path, "sendfile.txt")
    attachment_setup(tmp_path, "sendphoto.jpg")

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "attachments": [filepath],
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert "'attachments'" in str(mock_new_message.mock_calls)
    assert "'name': 'sendfile.txt'" in str(mock_new_message.mock_calls)

    filepath = attachment_setup(tmp_path, "sendfile.txt")
    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "attachments": [filepath],
                    "zip_attachments": True,
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert "'name': 'archive.zip'" in str(mock_new_message.mock_calls)

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "attachments": ["/config/sendfile.txt"],
                    "zip_attachments": True,
                    "zip_name": "zipfile",
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert "'name': 'zipfile.zip'" in str(mock_new_message.mock_calls)

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "photos": ["/config/sendphoto.jpg"],
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    assert "'name': 'sendphoto.jpg'" in str(mock_new_message.mock_calls)
    assert "'isInline': True" in str(mock_new_message.mock_calls)

    with patch("O365.connection.Connection.post") as mock_new_message:
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "photos": ["https://sendphoto.jpg"],
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_new_message.called
    print(mock_new_message.mock_calls)
    assert '<img src="https://sendphoto.jpg">' in str(mock_new_message.mock_calls)

    with (
        patch("O365.connection.Connection.post") as mock_new_message,
        pytest.raises(ValueError) as exc_info,
    ):
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {
                    "attachments": ["/config/nofile.txt"],
                },
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert not mock_new_message.called
    assert "Could not access file /config/nofile.txt at" in str(exc_info.value)


async def test_notify_failed_permission(
    hass: HomeAssistant,
    setup_update_integration,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test notify - HA Service."""
    entity_name = "sensor.test_mail"
    failed_perm = "mail.failed_perm"
    with patch(
        f"custom_components.{DOMAIN}.integration.notify_integration.PERM_MAIL_SEND",
        failed_perm,
    ):
        await hass.services.async_call(
            NOTIFY_DOMAIN,
            "ms365_mail_test",
            {
                "message": "Test message",
                "title": "Test title",
                "data": {"target": entity_name},
            },
            blocking=True,
            return_response=False,
        )
    assert (
        f"Not authorised to send mail - requires permission: {failed_perm}"
        in caplog.text
    )


def attachment_setup(tmp_path, infile):
    """Setup a token file"""
    fromfile = TEST_DATA_INTEGRATION_LOCATION / "files" / infile
    tofile = tmp_path / infile
    shutil.copy(fromfile, tofile)
    return tofile
