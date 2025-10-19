---
title: Permissions
nav_order: 3
---

# Permissions

This page details the permissions for this integration. General instructions can be found on the MS365 Home Assistant [Permissions](https://rogerselwyn.github.io/MS365-HomeAssistant/permissions.html) page.

*Note the requirement for `.Shared` permissions for shared mailboxes*

  | Feature   | Permissions                | Update | MS Graph Description                                           | Notes |
  |-----------|----------------------------|:------:|----------------------------------------------------------------|-------|
  | All       | offline_access             |        | *Maintain access to data you have given it access to*          |       |
  | All       | User.Read                  |        | *Sign in and read user profile*                                |       |
  | Mail      | Mail.Read                  |        | *Read access to user mail*                                     |       |
  | Notify    | Mail.Send                  | Y      | *Send mail as a user*                                          |       |
  | Mail      | Mail.Read.Shared           |        | *Read user and shared mail*                                    | For shared mailboxes |
  | Notify    | Mail.Send.Shared           | Y      | *Send mail on behalf of others*                                | For shared mailboxes |
  | AutoReply | MailboxSettings.ReadWrite  |        | *Read and write user mailbox settings*                         | Not for shared mailboxes |

