
from switch_control import SwitchControl

class GenericOnlyOnSwitch(SwitchControl):
    """Turn entity states on.

    Used for generic switches where all buttons should 
    set entity states on.
    """

    def handle_button_click(self, button_id):
        self.turn_on_entities(self.safe_click_entites(button_id))