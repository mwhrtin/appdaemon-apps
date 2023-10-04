
from switch_control import SwitchControl

class IkeaOnOffSwitch(SwitchControl):
    """Control lights on/off and dimmable brightness.

    Logics are built around the IKEA on/off switch.
    """

    def handle_button_click(self, button_id):
        if button_id == 1:
            self.turn_on_entities(self.safe_click_entites(button_id))
        elif button_id == 2:
            self.turn_off_entities(self.safe_click_entites(button_id))

    def handle_button_long_press(self, button_id):
        if button_id == 1:
            self.increase_brightness(self.safe_hold_to_dim_entities(button_id))
        elif button_id == 2:
            self.decrease_brightness(self.safe_hold_to_dim_entities(button_id))

    def handle_button_long_release(self, button_id):
        if button_id == 1:
            self.stop_brightness_change(self.safe_hold_to_dim_entities(button_id))
        elif button_id == 2:
            self.stop_brightness_change(self.safe_hold_to_dim_entities(button_id))

    def remap_button_id(self, button_id):
        if button_id == 'on':
            return 1
        elif button_id == 'off':
            return 2
        else: 
            return button_id