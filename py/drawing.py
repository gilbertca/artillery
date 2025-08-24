import turtle
import pdb

class Drawing:
    def __init__(self):
        turtle.bgcolor("#E5C287") # warm orange for testing
        self.turtle_namespace = {} # For easy turtle handling
        self.scale = 4 # map scale
        self.position_color = 'blue'
        self.target_color = 'red'
        self.map_color = 'black'
        self.min_radius_color = 'red'
        self.base_color = 'magenta'
        self.destination_color = 'purple'
        self.default_color = 'black'

    def draw_select_player_side_phase(self):
        # Draw all elements in the select player side phase:
        unit_button_args = (-100, 0, self.position_color, "Select unit side", "square")
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

        # Draw minimum radius (will be cleared after 'add_unit_phase' is over)
        min_radius_turtle = self.draw_minimum_radius()

        # Draw all positions (will be retained after 'add_unit_phase' is over)
        self.draw_all_units()

        # Draw the drag-to-drop add_unit_turtle
        add_unit_turtle = self.draw_add_unit_turtle()

        # Draw and return the end_unit_phase button (will be cleared after it is clicked / phase is over)
        end_unit_phase_button_args = (0, -120, self.default_color, "End add unit phase", "square")
        end_unit_phase_button = self.draw_button(*end_unit_phase_button_args)

        # Register all turtles for easy clearance:
        self.turtle_namespace.update(
            {
                'map_turtle': map_turtle,
                'add_unit_phase_turtles': [end_unit_phase_button, min_radius_turtle, add_unit_turtle]
                # 'add_unit_turtle' must be last, since 'add_unit' retrieves it via index '-1' - this is an arbitrary design detail
            }
        )

        # Return 'end_unit_phase_button' and 'add_unit_turtle' so the onclick events can be registered:
        return end_unit_phase_button, add_unit_turtle

    def draw_add_unit_turtle(self, x=0, y=120, color=None, text="Click and drag the unit to drop it on the map", add_unit_turtle=None):
        if color == None: color = self.default_color # self cannot be referenced in the method signature (i.e. color=self.default_color)
        # Create, setup the turtle:
        if add_unit_turtle == None: add_unit_turtle = turtle.Turtle()
        add_unit_turtle.hideturtle()
        add_unit_turtle.speed(0)
        add_unit_turtle.penup()

        # Configure color only (since the add_unit_turtle appears as the default arrow)
        add_unit_turtle.color(color)

        # Scale x and y values:
        x *= self.scale
        y *= self.scale

        # Draw add_unit_text, move the turtle to the correct locations:
        if text != "":
            add_unit_turtle.goto(x-20, y+20)
            add_unit_turtle.write(text)
        add_unit_turtle.goto(x, y)

        # Reveal and return the 'add_unit_turtle' so on-drag events can be registered to it:
        add_unit_turtle.showturtle()
        return add_unit_turtle

    def draw_button(self, x, y, color, text="", shape="square"):
        # Create, setup the turtle:
        button = turtle.Turtle()
        button.hideturtle()
        button.penup()

        # Scale x and y values, start moving the turtle:
        x *= self.scale
        y *= self.scale
        button.goto(x, y)

        # Configure shape, scale, color:
        button.color(color)
        button.shape(shape)
        button.shapesize(2, 4, 1) # Scale square -> rectangle

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
        map_turtle.speed(0)
        map_turtle.hideturtle()
        map_turtle.penup()

        # Draw the base, and the outer edge:
        base_circle_args = (0, 0, self.base_color, self.game_settings['base_radius'], map_turtle, 1)
        self.draw_circle(*base_circle_args)
        outer_circle_args = (0, 0, self.map_color, self.game_settings['map_radius'], map_turtle, 4)
        self.draw_circle(*outer_circle_args)
        
        return map_turtle

    def draw_minimum_radius(self):
        # Create, setup the turtle:
        min_radius_turtle = turtle.Turtle()
        min_radius_turtle.speed(0)
        min_radius_turtle.hideturtle()
        min_radius_turtle.penup()

        # Draw the minimum radius circle (only shown during the 'add_unit_phase')
        min_radius_args = (0, 0, self.min_radius_color, self.game_settings['minimum_unit_radius'], min_radius_turtle, 1)
        self.draw_circle(*min_radius_args)

        return min_radius_turtle

    def draw_all_units(self):
        return_position_turtles, return_destination_turtles = [], []
        # Query the API for updates to the units:
        self.update_unit_list()

        # Return the list of created (or pre-existing) turtles
        unit_turtles_list = self.turtle_namespace.get('position_turtles')
        if unit_turtles_list == None: unit_turtles_list = []

        # Iterate over all unit positions from the API;
        for position, destination in zip(self.units['positions'], self.units['destinations']):
            turtle_exists = False
            # Scale position and destination values:
            unit_position = (position['x'] * self.scale, position['y'] * self.scale)
            unit_destination = (destination['x'] * self.scale, destination['y'] * self.scale)

            # Iterate over all existing turtles; set 'turtle_exists' to True if a turtle exists at a position already:
            # (The first time this function is run, this for-loop is skipped)
            for unit_turtle in unit_turtles_list:
                turtle_position = unit_turtle.position()

                # If the unit exists at a location, we don't need to continue:
                if unit_position == turtle_position: 
                    turtle_exists = True
                    break # Break from inner for-loop after setting flag

            # If the turtle doesn't exist, we create it and append it to the list:
            # We also create the destination turtle
            if not turtle_exists:
                # Create, setup turtles:
                unit_turtle = turtle.Turtle()
                destination_turtle = turtle.Turtle()

                # Iterate over 'dry_turtles' to copy config for both turtles:
                for current_turtle, coordinates, color in zip(
                    (unit_turtle, destination_turtle),
                    (unit_position, unit_destination),
                    (self.position_color, self.destination_color)
                ):
                    current_turtle.hideturtle()
                    current_turtle.speed(0)
                    current_turtle.penup()
                    current_turtle.goto(*coordinates)
                    current_turtle.color(color)

                # Units face their destination, or the origin if the destinaion and position are the same
                if unit_position == unit_destination:
                    heading = unit_turtle.towards(0, 0)
                else:
                    heading = unit_turtle.towards(*unit_destination)
                unit_turtle.setheading(heading)
                destination_turtle.setheading(destination_turtle.towards(0, 0))

                # Reveal turtles; append to return lists
                unit_turtle.showturtle()
                destination_turtle.showturtle()
                return_position_turtles.append(unit_turtle)
                return_destination_turtles.append(destination_turtle)

        # Finish by returning the updated unit_turtle_list, and remapping the namespace:
        self.turtle_namespace.update({'position_turtles': return_position_turtles})
        self.turtle_namespace.update({'destination_turtles': return_destination_turtles})

    def draw_circle(self, x, y, color, radius, turtle, line_thickness):
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

