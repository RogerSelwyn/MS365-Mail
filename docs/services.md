---
title: Services
nav_order: 15
---

# Services

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