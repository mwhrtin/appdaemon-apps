
from switch_control import SwitchControl

class AqaraOppleSwitch(SwitchControl):
    """Control entity states on/off and dimmable brightness.

    Logics are built around the Aqara Opple switch.
    """

    def handle_button_click(self, button_id):
        self.toggle_entities(self.safe_click_entites(button_id))

    def handle_button_long_press(self, button_id):
        self.toggle_brightness_change(self.safe_hold_to_dim_entities(button_id))

    def handle_button_long_release(self, button_id):
        self.stop_brightness_change(self.safe_hold_to_dim_entities(button_id))