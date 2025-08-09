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

class Unit:
    def __init__(self, x, y, t):
        self.pos = (x, y)
        self.des = (x, y)
        self.t = t


class Target:
    def __init__(self, x, y, cost, t):
        self.pos = (x, y)
        self.cost = cost
        self.t = t


class Game:
    def __init__(self):
        self.units = []
        self.targets = []
        self.turtles = []
        # (0 = no side, 1 = unit side, 2 = target side)
        self.chosen_side = 0
        self.game_settings = {}
        self.t = None
        #self.t.color(MAP_COLOR)

    def Turtle(self):
        # We register each created turtle, so it may be conveniently cleared later
        t = turtle.Turtle()
        self.turtles.append(t)
        return t

    def clear_turtles(self):
        while len(self.turtles) != 0:
            t = self.turtles.pop()
            self._del_turtle(t)

    def _del_turtle(self, turtle):
            # Unfortunately, there is no clean way to *delete* a turtle from the canvas
            # see: https://github.com/python/cpython/issues/93642
            # This method instead hides all registered turtles, and removes all references to them
            # Essentially, one must pretend the turtle has been deleted
            turtle.reset()
            turtle.hideturtle()

    def get_game_settings(self):
        response = requests.get(f"{URL}/game").json()
        # API returns all strings; this step converts them to Python data types
        for key, value in response.items():
            self.game_settings.update({key: json.loads(value)})

    def get_player_side(self):
        # Clicking a turtle chooses the side
        unit_turtle = self.Turtle()
        target_turtle = self.Turtle()
        # DRY setup:
        for t in ((unit_turtle, -100, 0, UNIT_COLOR, self._pick_unit_side, "Choose unit side"),
                  (target_turtle, 100, 0, TARGET_COLOR, self._pick_target_side, "Choose target side")):
            i = t[0] # i = instance
            i.hideturtle() # From the doc: "hiding the turtle speeds up the drawing observably"
            i.penup()
            i.shapesize(2, 4, 1)
            i.shape("square")
            i.goto(t[1], t[2])
            i.color(t[3])
            i.onclick(t[4])
            i.write(t[5])
            i.goto(t[1], -20)
            i.showturtle() # Reveal turtle

    def _pick_unit_side(self, x, y):
        # self.chosen_side = 1 represents unit side
        self.chosen_side = 1
        self.clear_turtles()
        self.play()

    def _pick_target_side(self, x, y):
        # self.chosen_side = 2 represents target side
        self.chosen_side = 2
        self.clear_turtles()
        self.play()

    def draw_map(self):
        self.map_turtle = self.Turtle()
        self.map_turtle.speed(0)
        self._draw_circle(self.game_settings['map_radius'], "black") # Draw map
        self._draw_circle(self.game_settings['base_radius'], "magenta") # Draw base
        self.map_turtle.hideturtle()

    def _draw_circle(self, radius, color):
        self.map_turtle.hideturtle()
        self.map_turtle.penup()
        self.map_turtle.goto(0, 0)
        self.map_turtle.forward(SCALE*radius)
        self.map_turtle.left(90)
        self.map_turtle.pendown()
        self.map_turtle.color(color)
        self.map_turtle.showturtle()
        self.map_turtle.circle(SCALE*radius)

    def place_unit(self, x, y):
        x = x / SCALE
        y = y / SCALE
        response = requests.post(f"{URL}/units", json={'x': x, 'y': y})
        print(response.json())

    def play(self):
        self.draw_map()
        if self.chosen_side == 1: # Unit side
            self.unit_turtle = self.Turtle()
            self.unit_turtle.hideturtle()
            self.unit_turtle.penup()
            self.unit_turtle.left(90)
            self.unit_turtle.forward(SCALE * (self.game_settings['map_radius'] + 20))
            self.unit_turtle.write("Click and drag to place the unit on the map")
            self.unit_turtle.backward(20)
            self.unit_turtle.showturtle()
            self.unit_turtle.ondrag(self.unit_turtle.goto)
            self.unit_turtle.onrelease(self.place_unit)
        elif self.chosen_side == 2: # Artillery side
            pass

    def run(self):
        # Begin by updating game's settings (they might change between 'runs')
        self.get_game_settings()
        # Ask the user to choose a side:
        self.get_player_side()
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

