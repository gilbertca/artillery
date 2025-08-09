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
MAX_EXCEPTIONS = 3
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

    def clear_turtle(self, index):
        t = self.turtles.pop(index)
        t.reset()
        t.hideturtle()

    def clear_turtles(self):
        while len(self.turtles) != 0:
            t = self.turtles.pop()
            t.reset()
            t.hideturtle()

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
        while self.chosen_side == 0:
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

            # To create a non-blocking idle mode, we draw a circle (with a bit of magic to speed it up)
            t = self.Turtle()
            t.speed("fast")
            t.penup()
            t.forward(200)
            t.left(90)
            t.pendown()
            drawn = False
            while self.chosen_side == 0:
                if drawn: # the magic
                    t.speed("fastest")
                t.circle(200)
                drawn = True
        # Before control is returned to `self.run`, we cleanup:
        self.clear_turtles()

    def _pick_unit_side(self, x, y):
        # self.chosen_side = 1 represents unit side
        self.chosen_side = 1

    def _pick_target_side(self, x, y):
        # self.chosen_side = 2 represents target side
        self.chosen_side = 2

    def draw_map(self, chosen_side):
        pass

    def play(self):
        while True:
            # Draw play area:
            self.draw_map(self.chosen_side)

    def run(self):
        # Begin by updating game's settings (they might change between 'runs')
        self.get_game_settings()
        # Ask the user to choose a side:
        self.get_player_side()
        self.play()

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
    while True:
        # Attempt game
        try:
            game.run()
        # Only quit on KeyboardInterrupt (Ctrl+C)
        except KeyboardInterrupt:
            break
        # Print all other exceptions, quit after trying MAX_EXCEPTIONS times
        except Exception as e:
            print(e)
            if exception_count >= MAX_EXCEPTIONS:
                print(f"""

The program has encountered the maximum number of allowed,
unhandled exceptions ({MAX_EXCEPTIONS}). The program will now quit.

                """)
                break
            exception_count += 1

