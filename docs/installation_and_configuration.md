---
title: Installation and Configuration
nav_order: 4
---

# Installation and Configuration
This page details the configuration details for this integration. General instructions can be found on the MS365 Home Assistant [Installation and Configuration](https://rogerselwyn.github.io/MS365-HomeAssistant/installation_and_configuration.html) page.

### Configuration variables

Key | Type | Required | Description
-- | -- | -- | --
`entity_name` | `string` | `True` | Uniquely identifying name for the account. Mail entity names will be prefixed with this. `todo.{name}_mail`. Do not use email address or spaces.
`client_id` | `string` | `True` | Client ID from your Entra ID App Registration.
`client_secret` | `string` | `True` | Client Secret from your Entra ID App Registration.
`alt_auth_method` | `boolean` | `False` | If False (default), authentication is not dependent on internet access to your HA instance. [See Authentication](./authentication.md)
`enable_update` | `boolean` | `False` | If True (**default is False**), this will enable the notify service for sending emails
`shared_mailbox` | `string` | `False` | Email address or ID of shared mailbox *Only available for calendar and email sensors*

#### Advanced API Options

 These options will only be relevant for users in very specific circumstances.

 Key | Type | Required | Description
 -- | -- | -- | --
 `country` | `string` | `True` | Selection of an alternate country specific API. Currently only 21Vianet from China.

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
