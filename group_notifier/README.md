# group-notifier

## Description

An app used to send notifications to a group of user with the ability to filter the recipients based on their current zone from automations and blueprints. 

The notification is sent with a custom event sent from HomeAssistant using the format `notify.group@zone`:
```
notify.all            // send to recipients in group 'all' regardeless of their current zone.
notify.all@home       // send to recipients in group 'all' that are in zone 'home'.
notify.adults@work    // send to recipients in group 'adults' that are in zone 'work'.
notify.kids@not_home  // send to recipients in group 'kids' that are not in zone 'home'.
```

It's possible to specify if a reciepient should always receive notifications sent to a zone regardless if they are in the zone or not by using the `always_include_in` property.

**NOTE:** This was implemented for iOS and is only tested with iOS. Since the format for sending notifications to Android is different, Android is \*probably\* not supported.

## Usage

#### Define the recipient groups in the appdaemon's apps.yml:
Note that person 'John Doe' below will always receive notifications sent to `adults@home` regardless of his current zone when `always_include_in` is defined.

```
group_notifier:
  module: group_notifier
  class: GroupNotifier
  groups:
    all: 
      - notify: mobile_app_johns_iphone
        person: person.john_doe
      - notify: mobile_app_janes_iphone
        person: person.jane_doe 
      - notify: mobile_app_childs_iphone
        person: person.child_doe
    john: 
      - notify: mobile_app_johns_iphone
        person: person.john_doe
    adults: 
      - notify: mobile_app_johns_iphone
        person: person.john_doe
        always_include_in:
          - home
      - notify: mobile_app_janes_iphone
        person: person.jane_doe
    kids: 
      - notify: mobile_app_childs_iphone
        person: person.child_doe

```

#### Send notifications

Sample to send a notification to all recipients in the group `adults` that are currently in the zone `home`:
```
event: notify.all@home
event_data:
  title: House
  message: The washing machine is done.
  data:
    group: default_group
    tag: washing_machine_stopped
```

Sample blueprint to send notification with a temperature warning when a temperature sensor is below a lower limit. 

```
blueprint:
  name: 'Notificatio: temperature warning'
  description: Send a notificaiton when a temperature have reached a lower limit.
  domain: automation
  input:
    temperature_entity_id:
      name: Entity
      description: The entity that should be read.
      selector:
        entity:
          device_class: temperature
          domain: sensor
    temperature_limit_below:
      name: Lower temperature limit
      description: The lower temperature limit when a notification should be sent.
      default: '10.0'
      selector: 
        number:
          min: 0
          max: 40
          unit_of_measurement: '°C'
    group_notifier_event:
      name: Notification group
      description: The notification recipient
      selector:
        attribute:
          entity_id: group_notifier.events
    notification_tag:
      name: Tag
      description: The tag used to group multiple notifications.

trigger:
  - platform: numeric_state
    entity_id: !input temperature_entity_id
    below: !input temperature_limit_below
    for: 
      minutes: 2
    

variables:
  group_notifier_event: !input group_notifier_event
  notification_tag: !input notification_tag
  temperature_entity_id: !input temperature_entity_id
  temperature_limit_below: !input temperature_limit_below
  area_name: "{{ area_name(temperature_entity_id) }}"
  current_value: "{{ states(temperature_entity_id, rounded=True) }}"

action:
  event: !input group_notifier_event
  event_data:
    title: 'House'
    message: 'The temperature in {{ area_name|lower }} is below {{ current_value }}°C'
    data:
      group: 'default_group'
      tag: !input notification_tag
```