
import appdaemon.plugins.hass.hassapi as hass

BRIGHTNESS_DIRECTION_DOWN = "down"
BRIGHTNESS_DIRECTION_UP = "up"
BRIGHTNESS_TRANSITION_TIME = 25
BUTTON_PRESS = 0
BUTTON_CLICK = 2
BUTTON_LONG_PRESS = 1
BUTTON_LONG_RELEASE = 3
BUTTON_DOUBLE_CLICK = 4
BUTTON_TRIPPLE_CLICK = 5

class SwitchControl(hass.Hass):

    def initialize(self):
        self.device = self.args.get('device')

        self.click = self.buttons_from_argument('click')
        self.hold_to_dim = self.buttons_from_argument('hold_to_dim')

        self.last_brightness_direction = {}
        self.listen_event(self.handle_event, 'deconz_event')

    def handle_event(self, event_name, data, kwargs):
        """Manage new events.

        Keeps counters for button presses and resets counters on inactivity.
        """
        device_id = data['id']
        button_event = data['event']

        if device_id == self.device:
            #self.log("handle event: {}".format(data))
            self.handle_button_event(button_event)

    def handle_button_event(self, button_event):
        """Handle the button event and forward to the action method."""
        #self.log("handle button event: {}".format(button_event))
        button_action = button_event % 1000
        button_id = int((button_event - button_action) / 1000)
        
        if button_action == BUTTON_PRESS:
            pass
        elif button_action == BUTTON_CLICK:
            self.handle_button_click(button_id)
        elif button_action == BUTTON_LONG_PRESS:
            self.handle_button_long_press(button_id)
        elif button_action == BUTTON_LONG_RELEASE:
            self.handle_button_long_release(button_id)
        elif button_action == BUTTON_DOUBLE_CLICK:
            self.handle_button_double_click(button_id)
        elif button_action == BUTTON_TRIPPLE_CLICK:
            self.handle_button_double_click(button_id)

    def buttons_from_argument(self, argument):
        """Return a button dictionary from teh given argument."""
        dictionary = self.args.get(argument, dict())
        result = dict()
        for key, value in dictionary.items():
            result[self.remap_button_id(key)] = value

        return result

    def remap_button_id(self, button_id):
        """Return a remapped button id for the given button id."""
        return button_id

    def safe_click_entites(self, button_id):
        """Safely return the click entities for the given button id.

        If no entities are defined for the button id an empty list is returned.
        """
        if button_id in self.click:
            return self.click[button_id]
        else:
            return []

    def safe_hold_to_dim_entities(self, button_id):
        """Safely return the hold to dim entities for the given button id.

        If no entities are defined for the button id an empty list is returned.
        """
        if button_id in self.hold_to_dim:
            return self.hold_to_dim[button_id]
        else:
            return []


### Toggle on/off state ###

    def toggle_entities(self, list_of_entities):
        """Toggle the specified entities on/off."""
        if list_of_entities != None and len(list_of_entities) > 0:
            for entity in list_of_entities:
                if entity.startswith('light.'):
                    self.log("toggle {}".format(entity))
                    self.call_service('homeassistant/toggle', entity_id=entity)
                elif entity.startswith('switch.'):
                    self.log("toggle {}".format(entity))
                    self.call_service('homeassistant/toggle', entity_id=entity)
                else:
                    self.log("turn_on {}".format(entity))
                    self.call_service('homeassistant/turn_on', entity_id=entity)

    def turn_off_entities(self, list_of_entities):
        """Turn the specified entities off."""
        if list_of_entities != None and len(list_of_entities) > 0:
            for entity in list_of_entities:
                self.log("turn_off {}".format(entity))
                self.call_service('homeassistant/turn_off', entity_id=entity)

    def turn_on_entities(self, list_of_entities):
        """Turn the specified entities on."""
        if list_of_entities != None and len(list_of_entities) > 0:
            for entity in list_of_entities:
                self.log("turn_on {}".format(entity))
                self.call_service('homeassistant/turn_on', entity_id=entity)

### Control brightness ###

    def brightness_change(self, direction, list_of_entities):
        """Change the brightness either up or down for the specified light entities."""
        if list_of_entities != None and len(list_of_entities) > 0:

            transition_time = BRIGHTNESS_TRANSITION_TIME
            if direction == BRIGHTNESS_DIRECTION_UP:
                bri_inc = 254
            else:
                bri_inc = -254

            for entity in list_of_entities:
                if entity.startswith('light.'):
                    light_state = self.get_state(entity)
                    if light_state == "off":
                        self.call_service('homeassistant/turn_on', entity_id=entity)

                    self.log("deconz/configure bri_inc {value} @ {duration} ms {entity}".format(value=bri_inc, duration=transition_time, entity=entity))
                    self.call_service("deconz/configure", field="/state", entity=entity, data={"bri_inc": bri_inc, "transitiontime": transition_time})
                else:
                    pass

    def continue_brightness_change(self, list_of_entities):
        """Increase or decrease the brightness of the specified light entities based on the previous action."""
        key = "[ " + ", ".join(list_of_entities) + " ]"

        if key in self.last_brightness_direction:
            last_direction = self.last_brightness_direction[key]
        else: 
            last_direction = None 

        if last_direction is None:
            last_direction = BRIGHTNESS_DIRECTION_DOWN

        self.brightness_change(last_direction, list_of_entities)

    def decrease_brightness(self, list_of_entities):
        """Decrease the brightness of the specified light entities."""
        key = "[ " + ", ".join(list_of_entities) + " ]"
        direction = BRIGHTNESS_DIRECTION_DOWN
        self.last_brightness_direction[key] = direction
        self.brightness_change(direction, list_of_entities)

    def increase_brightness(self, list_of_entities):
        """Increase the brightness of the specified light entities."""
        key = "[ " + ", ".join(list_of_entities) + " ]"
        direction = BRIGHTNESS_DIRECTION_UP
        self.last_brightness_direction[key] = direction
        self.brightness_change(direction, list_of_entities)

    def stop_brightness_change(self, list_of_entities):
        """Stop the brightness change for the specified entities."""
        if list_of_entities != None and len(list_of_entities) > 0:
            for entity in list_of_entities:
                if entity.startswith('light.'):
                    light_state = self.get_state(entity)
                    if light_state == "off":
                        self.call_service('homeassistant/turn_on', entity_id=entity)

                    self.log("deconz/configure bri_inc 0 {}".format(entity))
                    self.call_service("deconz/configure", field="/state", entity=entity, data={"bri_inc": 0})
                else:
                    pass

    def toggle_brightness_change(self, list_of_entities):
        """Increase or decrease the brightness of the specified light entities based on the previous action."""
        key = "[ " + ", ".join(list_of_entities) + " ]"

        if key in self.last_brightness_direction:
            last_direction = self.last_brightness_direction[key]
        else: 
            last_direction = None 

        if last_direction is None:
            last_direction = BRIGHTNESS_DIRECTION_DOWN

        if last_direction == BRIGHTNESS_DIRECTION_UP:
            new_direction = BRIGHTNESS_DIRECTION_DOWN
        else:
            new_direction = BRIGHTNESS_DIRECTION_UP

        self.last_brightness_direction[key] = new_direction
        self.brightness_change(new_direction, list_of_entities)

    def toggle_brightness_direction(self, list_of_entities):
        """toggle the change brightness direction."""
        key = "[ " + ", ".join(list_of_entities) + " ]"

        if key in self.last_brightness_direction:
            last_direction = self.last_brightness_direction[key]
        else: 
            last_direction = None 

        if last_direction is None:
            last_direction = BRIGHTNESS_DIRECTION_DOWN

        if last_direction == BRIGHTNESS_DIRECTION_UP:
            new_direction = BRIGHTNESS_DIRECTION_DOWN
        else:
            new_direction = BRIGHTNESS_DIRECTION_UP

        self.last_brightness_direction[key] = new_direction

### Handle the various button press types ###

    def handle_button_long_press(self, button_id):
        """Handle long press for the given button id.

        The switch subclass need to implement this function 
        to add button long press handling.
        """
        pass

    def handle_button_long_release(self, button_id):
        """Handle long release for the given button id.

        The switch subclass need to implement this function 
        to add button long release handling.
        """
        pass

    def handle_button_click(self, button_id):
        """Handle click for the given button id.

        The switch subclass need to implement this function 
        to add button click handling.
        """
        pass

    def handle_button_double_click(self, button_id):
        """Handle double click for the given button id.
        
        The switch subclass need to implement this function 
        to add button double click handling.
        """
        pass

    def handle_button_tripple_click(self, button_id):
        """Handle tripple click for the given button id.
        
        The switch subclass need to implement this function 
        to add button tripple click handling.
        """
        pass

