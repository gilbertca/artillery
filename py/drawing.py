import turtle

class Drawing:
    def draw_select_player_side_phase(self):
        # Draw all elements in the select player side phase:
        unit_button = self.draw_button()
        target_button = self.draw_button()

        # Return the button turtles to 'select_player_side_phase'
        return unit_button, target_button

    def draw_button(self, x, y, color, text="", shape="square"):
        return None

    def draw_map(self):
        pass

    def draw_base(self):
        pass

    def draw_minimum_radius(self):
        pass

