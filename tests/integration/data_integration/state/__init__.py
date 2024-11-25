# pylint: disable=line-too-long
"""Tests for MS365 Mail."""

BASE_MESSAGES = [
    {
        "subject": "Subject1",
        "received": "2024-11-04T15:08:21+0000",
        "to": ["john@nomail.com"],
        "cc": [],
        "sender": "sender1@nomail.com",
        "has_attachments": True,
        "importance": "normal",
        "is_read": False,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
    },
    {
        "subject": "Subject2",
        "received": "2024-10-30T18:19:03+0000",
        "to": ["john@nomail.com"],
        "cc": ["cc_sender@nomail.com"],
        "sender": "sender2@nomail.com",
        "has_attachments": False,
        "importance": "normal",
        "is_read": True,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
    },
]

BASE_AUTOREPLY = {
    "internal_reply": "I'm currently on holiday",
    "external_reply": "I'm currently on holiday, please email Bob for answers",
    "external_audience": "all",
    "start": "2024-11-06T18:00:00+0000",
    "end": "2024-11-07T18:00:00+0000",
    "friendly_name": "test_autoreply",
}

CHILD_MESSAGES = [
    {
        "subject": "Subject3",
        "received": "2024-11-04T15:08:21+0000",
        "to": ["john@nomail.com"],
        "cc": [],
        "sender": "sender3@nomail.com",
        "has_attachments": True,
        "importance": "normal",
        "is_read": False,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
    }
]

SAFE_HTML_MESSAGES = [
    {
        "subject": "Subject1",
        "received": "2024-11-04T15:08:21+0000",
        "to": ["john@nomail.com"],
        "cc": [],
        "sender": "sender1@nomail.com",
        "has_attachments": True,
        "importance": "normal",
        "is_read": False,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "body": '<body lang="EN-GB" link="#467886" style="word-wrap:break-word" vlink="#96607D"><div class="WordSection1"><p class="MsoNormal"><span style="font-size:11.0pt">Some very simple test text</span></p></div></body>',
    },
    {
        "subject": "Subject2",
        "received": "2024-10-30T18:19:03+0000",
        "to": ["john@nomail.com"],
        "cc": ["cc_sender@nomail.com"],
        "sender": "sender2@nomail.com",
        "has_attachments": False,
        "importance": "normal",
        "is_read": True,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "body": "",
    },
]

CLEAN_HTML_MESSAGES = [
    {
        "subject": "Subject1",
        "received": "2024-11-04T15:08:21+0000",
        "to": ["john@nomail.com"],
        "cc": [],
        "sender": "sender1@nomail.com",
        "has_attachments": True,
        "importance": "normal",
        "is_read": False,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "body": "Some very simple test text",
    },
    {
        "subject": "Subject2",
        "received": "2024-10-30T18:19:03+0000",
        "to": ["john@nomail.com"],
        "cc": ["cc_sender@nomail.com"],
        "sender": "sender2@nomail.com",
        "has_attachments": False,
        "importance": "normal",
        "is_read": True,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "body": "",
    },
]

ATTACHMENT_MESSAGES = [
    {
        "subject": "Subject1",
        "received": "2024-11-04T15:08:21+0000",
        "to": ["john@nomail.com"],
        "cc": [],
        "sender": "sender1@nomail.com",
        "has_attachments": True,
        "importance": "normal",
        "is_read": False,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "attachments": ["test.jpg"],
    },
    {
        "subject": "Subject2",
        "received": "2024-10-30T18:19:03+0000",
        "to": ["john@nomail.com"],
        "cc": ["cc_sender@nomail.com"],
        "sender": "sender2@nomail.com",
        "has_attachments": False,
        "importance": "normal",
        "is_read": True,
        "flag": {
            "is_flagged": False,
            "is_completed": False,
            "due_date": None,
            "completion_date": None,
        },
        "attachments": [],
    },
]
