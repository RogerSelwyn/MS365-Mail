---
title: Permissions
nav_order: 3
---

# Permissions

Under "API Permissions" click Add a permission, then Microsoft Graph, then Delegated permission, and add the permissions as detailed in the list and table below:
  * Email - For an mail_sensor *Note the requirement for `.Shared` permissions for shared mailboxes*

   | Feature   | Permissions                | Update | MS Graph Description                                           | Notes |
   |-----------|----------------------------|:------:|----------------------------------------------------------------|-------|
   | All       | offline_access             |        | *Maintain access to data you have given it access to*          |       |
   | All       | User.Read                  |        | *Sign in and read user profile*                                |       |
   | Mail      | Mail.Read                  |        | *Read access to user mail*                                     |       |
   | Notify    | Mail.Send                  | Y      | *Send mail as a user*                                          |       |
   | Mail      | Mail.Read.Shared           |        | *Read user and shared mail*                                    | For shared mailboxes |
   | Notify    | Mail.Send.Shared           | Y      | *Send mail on behalf of others*                                | For shared mailboxes |
   | AutoReply | MailboxSettings.ReadWrite  |        | *Read and write user mailbox settings*                         | Not for shared mailboxes |
   

## Changing Features and Permissions
If you decide to enable new features in the integration, or decide to change from read only to read/write, you will very likely get a warning message similar to the following in your logs.

`Minimum required permissions not granted: ['Tasks.Read', ['Tasks.ReadWrite']]`

You will need to delete as detailed on the [token page](./token.md)
