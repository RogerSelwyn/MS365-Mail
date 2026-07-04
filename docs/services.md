---
title: Services
nav_order: 15
---

# Services

## Auto Reply Services
These services must be targeted at `auto_reply` sensors. 

### ms365_mail.set_auto_reply
Schedule the auto reply - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_mail.disable_auto_reply
Disable the auto reply - All parameters are shown in the available parameter list on the Developer Tools/Services tab.

#### Example enable auto reply service call

```yaml
service: ms365_mail.auto_reply_enable
target:
  entity_id: sensor.inbox
data:
  external_reply: I'm currently on holliday, please email Bob for answers
  internal_reply: I'm currently on holliday
  start: 2023-01-01T12:00:00+0000
  end: 2023-01-02T12:30:00+0000
  external_audience: all
```


## Mail Send Service
This services must be targeted at `mail` sensors. 

### ms365_mail.send_mail
Send an email - All parameters are shown in the available parameter list on the Developer Tools/Services tab.

#### Example send mail service call
```yaml
action: ms365_mail.mail_send
target:
  entity_id: sensor.my_mail
data:
  subject: Your Garage Door Friend
  message: The garage door has been open for 10 minutes.
  to:
    - joebloggs@hotmail.com
    - janebloggs@hotmail.com
  from: mgmt@noname.org.uk
  photos:
    - /config/documents/sendfile.txt
  attachments:
    - /config/documents/image.jpg
  importance: low
  message_is_html: true
  zip_attachments: true
  zip_name: zipfile.zip
```

##  Notify Service

### notify.ms365_mail_xxxxxxxx

#### Service data

Key | Type | Required | Description
-- | -- | -- | --
`message` | `string` | `True` | The email body
`title` | `string` | `False` | The email subject
`data` | `dict<data>` | `False` | Additional attributes - see table below

#### Extended data

Key | Type | Required | Description
-- | -- | -- | --
`target` | `string` | `False` | Recipient of the email, if not set will use the configured account's email address
`sender` | `string` | `False` | Sender of the email, if not set will use the configured account's email address - where the authenticated user has been delegated access to the mailbox
`message_is_html` | `boolean` | `False` | Is the message formatted as HTML
`importance` | `string` | `False` | Set importance to `low`, `normal` or `high`
`photos` | `list<string>` | `False` | File paths or URLs of pictures to embed into the email body
`attachments` | `list<string>` | `False` | File paths to attach to email
`zip_attachments` | `boolean` | `False` | Zip files from attachments into a zip file before sending
`zip_name` | `string` | `False` | Name of the generated zip file

#### Example notify service call

```yaml
service: notify.ms365_mail_xxxxxxxx
data:
  message: The garage door has been open for 10 minutes.
  title: Your Garage Door Friend
  data:
    target: joebloggs@hotmail.com
    sender: mgmt@noname.org.uk
    message_is_html: true
    attachments:
      - "/config/documents/sendfile.txt"
    zip_attachments: true
    zip_name: "zipfile.zip"
    photos:
      - "/config/documents/image.jpg"
```

You can send to multiple targets by structuring the target value as a list.
```yaml
service: notify.ms365_mail_xxxxxxxx
data:
  message: The garage door has been open for 10 minutes.
  title: Your Garage Door Friend
  data:
    target: 
      - joebloggs@hotmail.com
      - janeblogs@hotmail.com

```