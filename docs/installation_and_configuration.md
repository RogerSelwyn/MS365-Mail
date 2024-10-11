---
title: Installation and Configuration
nav_order: 4
---

# Installation and Configuration
## Installation
1. Ensure you have followed the [prerequisites instructions](./prerequisites.md)
    * Ensure you have a copy of the Client ID and the Client Secret **Value** (not the ID)
1. Optionally you can set up the [permissions](./permissions.md), alternatively you will be requested to approve permissions when you authenticate to MS 365.
1. Install this integration:
    * Recommended - see below, or
    * Manually - Copy [these files](https://github.com/RogerSelwyn/MS365-ToDo/tree/main/custom_components/ms365_mail) to custom_components/ms365_mail/.
1. Restart your Home Assistant instance to enable the integration
1. Add the integration via the `Devices & Services` dialogue. Follow the instructions in the install process (or see [Authentication](./authentication.md)) to establish the link between this integration and the Entra ID App Registration
    * A persistent token will be created in the hidden directory config/ms365_storage/.MS365-token-cache

**Note** If your installation does not complete authentication, or the sensors are not created, please go back and ensure you have accurately followed the steps detailed, also look in the logs to see if there are any errors. You can also look at the [errors page](./errors.md) for some other possibilities.

**Note** To configure a second account, add the integration again via the `Devices & Services` dialogue.

### HACS

1. Launch HACS
1. Navigate to the Integrations section
1. Add this repository as a Custom Repository (Integration) via the menu at top right.
1. Search for "Microsoft 365 Mail"
1. Select "Install this repository"
1. Restart Home Assistant


### Configuration variables

Key | Type | Required | Description
-- | -- | -- | --
`entity_name` | `string` | `True` | Uniquely identifying name for the account. Mail entity names will be prefixed with this. `todo.{name}_mail`. Do not use email address or spaces.
`client_id` | `string` | `True` | Client ID from your Entra ID App Registration.
`client_secret` | `string` | `True` | Client Secret from your Entra ID App Registration.
`alt_auth_method` | `boolean` | `False` | If False (default), authentication is not dependent on internet access to your HA instance. [See Authentication](./authentication.md)
`enable_update` | `boolean` | `False` | If True (**default is False**), this will enable the notify service for sending emails
`shared_mailbox` | `string` | `False` | Email address or ID of shared mailbox *Only available for calendar and email sensors*

### Options variables

Key | Type | Required | Description
-- | -- | -- | --
`folder` | `string` | `False` | Mail folder to monitor, for nested calendars separate with '/' ex. "Inbox/SubFolder/FinalFolder" Default is Inbox
`max_items` | `integer` | `False` | Max number of items to retrieve (default 5)
`is_unread` | `boolean` | `False` | True=Only get unread, False=Only get read, Not set=Get all
`from` | `string` | `False` | Only retrieve emails from this email address
`has_attachment` | `boolean` | `False` | True=Only get emails with attachments, False=Only get emails without attachments, Not set=Get all
`importance` | `string` | `False` | Only get items with 'low'/'normal'/'high' importance
`subject_contains` | `string` | `False` | Only get emails where the subject contains this string (Mutually exclusive with `subject_is`)
`subject_is` | `string` | `False` | Only get emails where the subject equals exactly this string (Mutually exclusive with `subject_contains`)
`download_attachments` | `boolean` | `False` | **True**=Show attachment names on entity, False=Don't show attachment names on entity - Increases data usage
`save_attachments` | `boolean` | `False` | True=Save attachments (to ms365_storage/attachments), **False**=Don't save attachments - Increases data usage
`html_body` | `boolean` | `False` | True=Output HTML body, **False**=Output plain text body
`show_body` | `boolean` | `False` | **True**=Show body on entity, False=Don't show body on entity
`body_contains` | `string` | `False` | Only get emails where the body contains this string