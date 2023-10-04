
from switch_control import SwitchControl

class HueSmartButton(SwitchControl):
    """Control entity states on/off and dimmable brightness.

    Logics are built around the Hue Smart Button.
    """

    def handle_button_click(self, button_id):
        self.toggle_entities(self.safe_click_entites(button_id))

    def handle_button_long_press(self, button_id):
        self.continue_brightness_change(self.safe_hold_to_dim_entities(button_id))

    def handle_button_long_release(self, button_id):
        self.toggle_brightness_direction(self.safe_hold_to_dim_entities(button_id))
        self.stop_brightness_change(self.safe_hold_to_dim_entities(button_id))

    def remap_button_id(self, button_id):
        return 1