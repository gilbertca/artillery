import requests
import argparse
import json
import time
import turtle

# TODO: Semi-Dynamic screen-widths
# TODO: Finish map drawing functions
BG_COLOR = "#E5C287"
turtle.bgcolor(BG_COLOR)
# Globals
URL = None
SCALE = 3
UNIT_COLOR = 'blue'
TARGET_COLOR = 'red'
MAP_COLOR = 'black'

class Game:
    def __init__(self):
        self.units = []
        self.targets = []
        self.turtles = []
        # (0 = no side, 1 = unit side, 2 = target side)
        self.chosen_side = 0
        self.game_settings = {}
        self.unit_turtle = None
        self.target_turtle = None
        self.map_turtle = None

    def Turtle(self):
        # We register each created turtle, so it may be conveniently cleared later
        t = turtle.Turtle()
        self.turtles.append(t)
        return t

    def _process_response_json(self, response):
        # Some magic to convert (most) strings to Python objects:
        return_values = {}
        for key, value in response.items():
            return_values.update({key: json.loads(value)})
        return return_values

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

    def get_game_settings(self):
        response = requests.get(f"{URL}/game").json()
        game_settings = self._process_response_json(response)
        self.game_settings.update(game_settings)

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

    def draw_map(self):
        self.map_turtle = self.Turtle()
        self.map_turtle.speed(0)
        self._draw_circle(self.map_turtle, self.game_settings['map_radius'], "black", thickness=4) # Draw map
        self._draw_circle(self.map_turtle, self.game_settings['base_radius'], "magenta", thickness=8) # Draw base
        self.map_turtle.hideturtle()

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

    def place_unit(self, x, y):
        x = x / SCALE
        y = y / SCALE
        response = requests.post(f"{URL}/units", json={'x': x, 'y': y})
        data = response.json()
        self.draw_add_unit_phase()

    def place_target(self, x, y):
        pass # DRY with `place_unit` function, since they are similar API calls

    def draw_add_unit_phase(self, first_run=False):
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
            self.unit_turtle.onrelease(self.place_unit) # (6) Control is passed to place_unit OR
            # End unit phase button:
            pass # (9?) Control is passed to set_destination_phase
        # All iterations except the first
        else: # Runs when control is passed from place_unit
            # Go to "Final position" from previous if statement (we reset the unit_turtle each time)
            self.unit_turtle.home()
            self.unit_turtle.left(90)
            self.unit_turtle.forward(SCALE * (self.game_settings['map_radius']) + 40) # 60 forward, 20 back = 40 forward
        self.unit_turtle.showturtle()

    def play(self):
        self.draw_map()
        if self.chosen_side == 1: # Unit side
            self.unit_turtle = self.Turtle()
            self.draw_add_unit_phase(first_run=True) # (5) Control is passed to draw_add_unit_phase

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

