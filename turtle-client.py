import requests
import argparse
import math
import json
import time
import turtle

# TODO: Semi-Dynamic screen-widths
# TODO: Finish map drawing functions
BG_COLOR = "#E5C287"
turtle.bgcolor(BG_COLOR)
# Globals
URL = None
SCALE = 4
UNIT_COLOR = 'blue'
TARGET_COLOR = 'red'
MAP_COLOR = 'black'

class API:
    """
    Logical grouping for functions related to the *API*
    """
    def _process_response_json(self, response):
        # Some magic to convert (most) strings to Python objects:
        return_values = {}
        for key, value in response.items():
            return_values.update({key: json.loads(value)})
        return return_values

    def get_game_settings(self):
        response = requests.get(f"{URL}/game").json()
        game_settings = self._process_response_json(response)
        self.game_settings.update(game_settings)

    def add_unit(self, x, y):
        # This function is only ever called during the add_unit phase
        x = x / SCALE
        y = y / SCALE
        response = requests.post(f"{URL}/units", json={'x': x, 'y': y})
        data = response.json()
        self.add_unit_phase()

    def set_destination(self, x, y):
        pass


class DrawingFunctions:
    """
    Logical grouping for functions related to *drawing*
    """
    def clear_turtles(self):
        while len(self.turtles) != 0:
            t = self.turtles.pop()
            self._del_turtle(t)

    def _del_turtle(self, turtle):
            # Unfortunately, there is no clean way to *delete* a turtle from the canvas
            # see: https://github.com/python/cpython/issues/93642
            # This method instead hides all registered turtles, and removes all references to them
            # Essentially, one must pretend the turtle has been deleted
            turtle.clear()
            turtle.hideturtle()

    def draw_button(self, turtle, x, y, color, callback, text="", shape="square", text_pad=-20):
        turtle.hideturtle() # From the doc: "hiding the turtle speeds up the drawing observably"
        turtle.penup()
        turtle.shapesize(2, 4, 1)
        turtle.shape(shape)
        turtle.goto(x, y)
        turtle.color(color)
        turtle.onclick(callback)
        turtle.write(text)
        turtle.goto(x, y+text_pad)
        turtle.showturtle() # Reveal turtle

    def draw_map(self):
        self.map_turtle = turtle.Turtle()
        self.map_turtle.speed(0)
        self._draw_circle(self.map_turtle, self.game_settings['map_radius'], "black", thickness=4) # Draw map
        self._draw_circle(self.map_turtle, self.game_settings['base_radius'], "magenta", thickness=8) # Draw base
        self.map_turtle.hideturtle()

    def draw_all_positions(self):
        # Get data for all units:
        response = requests.get(f"{URL}/units").json()
        data = self._process_response_json(response)
        positions = data['positions']
        destinations = data['destinations']
        # Draw units facing destinations:
        for position, destination in zip(positions, destinations):
            x = travel_x = destination['x'] - position['x']
            y = travel_y = destination['y'] - position['y']
            scaled_linear_distance = True
            # If x and y are 0, then the position and destination are the same
            # The turtle should instead point at the origin
            if travel_x == 0.0 and travel_y == 0.0:
                x = position['x']
                y = position['y']
                scaled_linear_distance = False
            position_turtle = self.Turtle(position['x'] * SCALE, position['y'] * SCALE)
            position_turtle.setheading(180.0 + math.degrees(math.atan2(y, x)))
            # To create the destination turtle: copy the position turtle,
            # and move it 'scaled_linear_distance' forward while tracing a line
            destination_turtle = self.clone_turtle(position_turtle)
            if scaled_linear_distance: # Move trace movement:
                scaled_linear_distance = math.sqrt(x*x + y*y) * SCALE
                destination_turtle.pendown()
                destination_turtle.forward(scaled_linear_distance)
                destination_turtle.setheading(180.0 + math.degrees(math.atan2(destination['y'], destination['x'])))
            destination_turtle.color("red")
            destination_turtle.ondrag(destination_turtle.goto) # destination_turtle follows the cursor
            destination_turtle.onrelease(self.set_destination) # dropping the turtle sets the destination

    def draw_all_destinations(self):


    def _draw_circle(self, turtle, radius, color, thickness=1):
        turtle.hideturtle()
        turtle.penup()
        turtle.home()
        turtle.speed(0)
        turtle.pensize(thickness)
        turtle.forward(SCALE*radius)
        turtle.left(90)
        turtle.pendown()
        turtle.color(color)
        turtle.showturtle()
        turtle.circle(SCALE*radius)
        turtle.penup()


class Game(DrawingFunctions, API):
    def __init__(self):
        self.unit_coords = [] # unit positions
        self.dest_coords = [] # unit destinations
        self.target_coords = [] # target destinations
        self.costs = [] # target costs
        self.turtles = [] # registered turtles

        # (0 = no side chosen, 1 = unit side, 2 = target side)
        self.chosen_side = 0
        self.phase = None
        self.game_settings = {} # game settings from API

        # Unregistered Turtles:
        self.unit_turtle = None
        self.target_turtle = None
        self.map_turtle = None

    def Turtle(self, x=None, y=None):
        # We register each created turtle, so it may be conveniently cleared later
        t = turtle.Turtle()
        t.speed(0)
        t.penup()
        if x is not None and y is not None: # useful shortcut
            t.goto(x, y)
        self.turtles.append(t)
        return t

    def clone_turtle(self, t):
        # Register cloned turtle
        clone = t.clone()
        self.turtles.append(clone)
        return clone

    def get_player_side(self):
        # Clicking a turtle chooses the side
        unit_button_turtle = self.Turtle()
        target_button_turtle = self.Turtle()
        # DRY setup:
        for t in (
            (unit_button_turtle, -100, 0, UNIT_COLOR, self._pick_unit_side, "Choose unit side"),
            (target_button_turtle, 100, 0, TARGET_COLOR, self._pick_target_side, "Choose target side")
        ):
            self.draw_button(*t) # (2) Control is passed to _pick_[unit/target]_side

    def _pick_unit_side(self, x, y):
        # self.chosen_side = 1 represents unit side
        self.chosen_side = 1
        self.clear_turtles()
        self.play() # (3) Control is passed to play

    def _pick_target_side(self, x, y):
        # self.chosen_side = 2 represents target side
        self.chosen_side = 2
        self.clear_turtles()
        self.play() # (4) Control is passed to play

    def place_target(self, x, y):
        pass # DRY with `add_unit` function, since they are similar API calls

    def add_unit_phase(self, first_run=False):
        # Cautious setup:
        self.unit_turtle.hideturtle()
        self.unit_turtle.penup()
        # First time setup:
        if first_run: # Runs when control is passed from play
            # Draw minimum radius circle:
            self._draw_circle(self.unit_turtle, self.game_settings['minimum_unit_radius'], "red")
            # Draw text:
            self.unit_turtle.home()
            self.unit_turtle.left(90)
            self.unit_turtle.color("black")
            self.unit_turtle.forward(SCALE * self.game_settings['map_radius'] + 60)
            self.unit_turtle.write("Click and drag to place the unit on the map")
            # Final position:
            self.unit_turtle.backward(20)
            # Functions for unit_turtle (drag and drop new units):
            self.unit_turtle.ondrag(self.unit_turtle.goto)
            self.unit_turtle.onrelease(self.add_unit) # (6) Control is passed to add_unit OR (9)
            # End unit phase button:
            self.end_phase_turtle = self.Turtle()
            # (9) Control is passed to set_destination_phase
            self.draw_button(self.end_phase_turtle, 0, -100, MAP_COLOR, self.set_destination_phase, "End add unit phase"),
        # All iterations except the first
        else: # Runs when control is passed from add_unit
            # Go to "Final position" from previous if statement (we reset the unit_turtle each time)
            self.unit_turtle.home()
            self.unit_turtle.left(90)
            self.unit_turtle.forward(SCALE * (self.game_settings['map_radius']) + 40) # 60 forward, 20 back = 40 forward
        self.draw_all_units()
        self.unit_turtle.showturtle()

    def set_destination_phase(self, _x, _y):
        self.clear_turtles()

    def play(self):
        self.draw_map()
        if self.chosen_side == 1: # Unit side
            self.unit_turtle = self.Turtle()
            self.add_unit_phase(first_run=True) # (5) Control is passed to add_unit_phase

    def run(self):
        # Begin by updating game's settings (they might change between 'runs')
        self.get_game_settings()
        # Ask the user to choose a side:
        self.get_player_side() # (1) Control is passed to get_player_side
        # Begin the main loop:
        # see: https://stackoverflow.com/questions/39429227/turtle-graphics-python-mainloop/41205497#41205497
        turtle.mainloop()

if __name__ == "__main__":
    # Setup arguments:
    parser = argparse.ArgumentParser(
            description='A client written with Python\'s turtle for the Artillery game.')
    parser.add_argument('--url', type=str, required=True)
    args = parser.parse_args()
    URL = args.url

    # Create game, main loop:
    game = Game()
    exception_count = 0
    game.run()

