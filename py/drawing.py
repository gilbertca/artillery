import turtle

class Drawing:
    def __init__(self):
        turtle.bgcolor("#E5C287") # warm orange for testing
        self.turtle_namespace = {} # For easy turtle handling
        self.scale = 3 # map scale
        self.unit_color = 'blue'
        self.target_color = 'red'
        self.map_color = 'black'
        self.base_color = 'magenta'
        self.default_color = 'black'

    def draw_select_player_side_phase(self):
        # Draw all elements in the select player side phase:
        unit_button_args = (-100, 0, self.unit_color, "Select unit side", "square")
        unit_button = self.draw_button(*unit_button_args)
        target_button_args = (100, 0, self.target_color, "Select target side", "square")
        target_button = self.draw_button(*target_button_args)

        # Register the buttons for easy clearance:
        self.turtle_namespace.update({'select_player_side_phase_buttons': [unit_button, target_button]})

        # Return the button turtles to 'select_player_side_phase'
        return unit_button, target_button

    def draw_add_unit_phase(self):
        # Draw the permanent map surface:
        map_turtle = self.draw_map()

        # Draw all positions (will be retained after 'add_unit_phase' is over)
        unit_turtles_list = self.draw_all_units()

        # Draw minimum radius (will be cleared after 'add_unit_phase' is over)
        min_radius_turtle = self.draw_minimum_radius()
        # Draw and return the end_unit_phase button (will be cleared after it is clicked / phase is over)
        end_unit_phase_button_args = (0, -100, self.default_color, "End add unit phase", "square")
        end_unit_phase_button = self.draw_button(*end_unit_phase_button_args)
        
        # Register all turtles for easy clearance:
        self.turtle_namespace.update(
            {
                'map_turtle': map_turtle,
                'unit_turtles': unit_turtles_list,
                'add_unit_phase_turtles': [end_unit_phase_button, min_radius_turtle]
            }
        )

        # Return 'end_unit_phase_button' so the onclick event can be registered:
        return end_unit_phase_button

    def draw_button(self, x, y, color, text="", shape="square"):
        # Create, setup the turtle:
        button = turtle.Turtle()
        button.hideturtle()
        button.penup()

        # Scale x and y values, start moving the turtle
        x *= self.scale
        y *= self.scale
        button.goto(x, y)

        # Configure shape, scale, color:
        button.color(color)
        button.shape(shape)
        button.shapesize(2, 4, 1) # Scale Square -> Rectangle

        # Draw text if applicable:
        if text != "":
            button.goto(x-20, y+20)
            button.write(text)
            button.goto(x, y)

        # Reveal and return:
        button.showturtle()
        return button

    def draw_map(self):
        # Create, setup the turtle:
        map_turtle = turtle.Turtle()
        map_turtle.hideturtle()
        map_turtle.penup()

        # Draw the base, and the outer edge:
        base_circle_args = (0, 0, self.base_color, self.game_settings['base_radius'], map_turtle)
        self.draw_circle(*base_circle_args)
        outer_circle_args = (0, 0, self.map_color, self.game_settings['map_radius'], map_turtle)
        self.draw_circle(*outer_circle_args)
        
        return map_turtle

    def draw_minimum_radius(self):
        # Create, setup the turtle:
        min_radius_turtle = turtle.Turtle()
        min_radius_turtle.hideturtle()
        min_radius_args = (0, 0, self.min_radius_color)

    def draw_all_units(self):
        pass

    def draw_circle(self, x, y, color, radius, turtle, line_thickness=1):
        # Scale circle:
        radius = self.scale * radius

        # Travel to circle start:
        turtle.penup()
        turtle.goto(x, y)
        turtle.setheading(0)
        turtle.forward(radius)
        turtle.setheading(90)

        # Configure pen properties:
        turtle.pendown()
        turtle.color(color)
        turtle.pensize(line_thickness)

        # Draw the circle:
        turtle.circle(radius)

    def hide_turtles(self, namespace_key):
        for turtle in self.turtle_namespace[namespace_key]:
            turtle.reset()
            turtle.hideturtle()

