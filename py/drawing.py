import turtle


class Drawing:
    def __init__(self, *args, **kwargs):
        super().__init__()
        turtle.bgcolor("#E5C287") # warm orange for testing
        self.scale = 4
        self.unit_color = 'blue'
        self.target_color = 'red'
        self.map_color = 'black'

    def draw_select_player_side_phase(self):
        # Draw all elements in the select player side phase:
        unit_button_args = (-100, 0, self.unit_color, "Select unit side", "square")
        unit_button = self.draw_button(*unit_button_args)
        target_button_args = (100, 0, self.target_color, "Select target side", "square")
        target_button = self.draw_button(*target_button_args)

        # Return the button turtles to 'select_player_side_phase'
        return unit_button, target_button

    def draw_button(self, x, y, color, text="", shape="square"):
        # Create and move the turtle:
        button = turtle.Turtle()
        button.hideturtle()
        button.penup()
        button.goto(x, y)

        # Configure shape and scale:
        # Draw text if applicable:
        # Reveal and return:
        button.showturtle()
        return button

    def draw_map(self):
        pass

    def draw_base(self):
        pass

    def draw_minimum_radius(self):
        pass

