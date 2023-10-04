
from switch_control import SwitchControl

class GenericToggleStateSwitch(SwitchControl):
    """Toggle entity states on/off.

    Used for generic switches where all buttons should 
    toggle entity states on/off.
    """

    def handle_button_click(self, button_id):
        self.toggle_entities(self.safe_click_entites(button_id))