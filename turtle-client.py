import requests
import argparse
import turtle
import math
import json
import time

from py.api import API
from py.drawing import Drawing

class Game(Drawing, API):
    def __init__(self, url):
        # Explicit mixin initialization:
        Drawing.__init__(self)
        API.__init__(self, url)

        self.game_settings = {} # from /game endpoint
        self.player_side = 0 # 0 = no side chosen, 1 = unit side chosen, 2 = target side chosen

    def update_game_settings(self):
        self.game_settings.update(self.query_api('game', 'get'))

    def run(self):
        self.update_game_settings()

        # (1) Control is passed to 'select_player_side_phase'
        self.select_player_side_phase()

    def select_player_side_phase(self):
        # (2) Control is received from 'run'
        # Draw the screen:
        unit_button, target_button = self.draw_select_player_side_phase()

        # Point the buttons to their functions:
        unit_button.onclick(self.choose_player_side)
        target_button.onclick(self.choose_player_side)

        # At this point, all initial setup is complete, and control can be passed to tk
        turtle.mainloop()
        # (3) Control is passed to 'choose_player_side' for both buttons

    def choose_player_side(self, x, y):
        # (4) Control is received from button clicks from 'select_player_side_phase'
        if x < 0: # Left side is for unit player
            self.player_side = 1
            # (5A) Control is passed to 'add_unit_phase' OR
            self.add_unit_phase()
        elif x > 0: # Right side is for target player
            self.player_side = 2
            # OR (5B) Control is passed to 'add_target_phase'
            self.add_target_phase()

    def add_unit_phase(self):
        # (6A) Control is received from 'choose_player_side'
        # Start by cleaning up 'select_player_side_phase_buttons' buttons:
        self.hide_turtles('select_player_side_phase_buttons')

        # Point the end_phase_button to the next phase 'set_destination_phase':
        end_phase_button = self.draw_add_unit_phase()
        # (7A) Control is passed to 'set_destination_phase'
        end_phase_button.onclick(self.set_destination_phase)

    def set_destination_phase(self, _x, _y):
        # _x and _y are required since 'onclick' passes an x and y coordinate
        # Start by cleaning up 'add_unit_phase_temporary_turtles':
        self.hide_turtles('add_unit_phase_turtles')

    def add_target_phase(self):
        pass

if __name__ == "__main__":
    # Setup arguments:
    parser = argparse.ArgumentParser(
            description="A client written with Python's turtle for the Artillery game.")
    parser.add_argument("--url", type=str, required=True)
    args = parser.parse_args()
    url = args.url

    # Create game, main loop:
    game = Game(url)
    game.run()

