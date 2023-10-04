
from switch_control import SwitchControl

class GenericOnlyOffSwitch(SwitchControl):
    """Turn entity states off.

    Used for generic switches where all buttons 
    should set entity states off.
    """

    def handle_button_click(self, button_id):
        self.turn_on_entities(self.safe_click_entites(button_id))