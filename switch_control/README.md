# switch_control

## Description

This is an app used to map Zigbee switches and remote controls to entities (lights, switches, groups) when using the [deCONZ integration](https://www.home-assistant.io/integrations/deconz/). 

#### Events and functionality

The compatability depends on the device, but the app itself is able to support the following events: 
- Press
- Long press
- Long release
- Click
- Double click
- Triple click


The app also support a "hold to dim" functionality where a light is continoulsy dimmed up or down while a button is pressed and hold.

#### The follow devices are implemented:

- **Aqara Opple Switch**: All buttons toggle `on/off`, long press to change brightness.
- **Hue Dimmer Switch**: All buttons toggle `on/off`, long press to change brightness.
- **Hue Smart Button**: Button toggle `on/off`, long press to change brightness.
- **IKEA On/Off Switch**: Rocker is mapped to `on` and `off`. Long press `on` will increase brightness, long press `off` will decrease the brightness. 
 
#### Generic implementations:
- **GenericOnlyOffSwitch**: All buttons on the device will turn `off`.
- **GenericOnlyOnSwitch**: All buttons on the device will turn `on`.
- **GenericToggleStateSwitch**: All buttons on the device toggles `on/off`.
## Usage

#### Sample using the "Aqara Opple Switch" implementation:
```
opple_switch_1:
  dependencies: switch_control
  module: aqara_opple_switch
  class: AqaraOppleSwitch
  device: zigbee_xiaomi_opple_wxcjkg13lm_1
  click:
    1:
      - light.reading_lamp
    2: 
      - light.floor_lamp
    3: 
      - switch.shelf_lamp
    4: 
      - light.table_lamp_1
      - light.table_lamp_2
    5: 
      - none
    6:     
      - none
```

#### Sample using the generic "always on" implementation:
```
ikea_on_off_switch_1:
  dependencies: switch_control
  module: generic_only_on_switch
  class: GenericOnlyOnRemote
  device: zigbee_ikea_on_off_switch_1
  click:
    1:
      - group.my_morning_lights
    2:
      - group.my_morning_lights
```
#### Sample using the "Hue Smart Button" implementation:

```
hue_smart_button_1:
  dependencies: switch_control
  module: hue_smart_button
  class: HueSmartButton
  device: philips_smart_button_1
  click:
    1:
      - light.library_reading_lamp_1
  hold_to_dim:
    1:
      - light.library_reading_lamp_1
```

## Disclaimer

This app is heavily based on the work done by [Kane610](https://github.com/Kane610) and his [remote_control app](https://github.com/Kane610/appdaemon-apps/blob/a08097a717c4b219850978931f9231b1fb4edd7b/remote_control.py).


