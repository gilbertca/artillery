from argparse import ArgumentParser
# TODO: The various buttons, objects, and units, should be represented as subclasses of Turtle, which allows us to extend the 'onclick' 'onrelease' and 'ondrag' functions to include more arguments
from turtle import mainloop
from turtle import Turtle

from py.api import API
from py.drawing import Drawing

class Game(Drawing, API):
    def __init__(self, url):
        # Explicit mixin initialization:
        Drawing.__init__(self)
        API.__init__(self, url)

        self.game_settings = {} # from /game endpoint
        self.units = {} # from /units endpoint
        self.player_side = 0 # 0 = no side chosen, 1 = unit side chosen, 2 = target side chosen

    def update_game_settings(self):
        self.game_settings.update(self.query_api('game', 'get'))

    def update_unit_list(self):
        self.units.update(self.query_api('units', 'get'))

    def run(self):
        self.update_game_settings()

        # (1) Control is passed to 'select_player_side_phase'
        self.select_player_side_phase()

    def select_player_side_phase(self):
        # (2) Control is received from 'run'
        # Draw the screen:
        unit_button, target_button = self.draw_select_player_side_phase()

        # Point the buttons to their functions:
        unit_button.onclick(partial(self.choose_player_side, )
        target_button.onclick(self.choose_player_side)

        # At this point, all initial setup is complete, and control can be passed to tk
        mainloop()
        # (3) Control is passed to 'choose_player_side' for both buttons

    def choose_player_side(self, _x, _y, player_side_int):
        # (4) Control is received from button clicks from 'select_player_side_phase'
        self.player_side = player_side_int
        # (5A) Control is passed to 'add_unit_phase' OR
        # OR (5B) Control is passed to 'add_target_phase'
        if player_side_int == 1:
            self.add_unit_phase()
        elif player_side_int == 2:
            self.add_target_phase()
        else:
            raise ValueError(f"choose_player side received a value of {player_side_int}, for 'player_side_int'. This value should be equal to 1 or 2.")

    def add_unit_phase(self):
        # (6A) Control is received from 'choose_player_side'
        # Start by cleaning up 'select_player_side_phase_buttons' buttons:
        self.hide_turtles('select_player_side_phase_buttons')

        # Draw the add_unit_phase; create the interactive turtles:
        end_phase_button, add_unit_turtle = self.draw_add_unit_phase()
        # 'add_unit_turtle' allows dragging and dropping units
        add_unit_turtle.ondrag(add_unit_turtle.goto)
        add_unit_turtle.onrelease(self.add_unit)
        # (7A) Control is passed to 'set_destination_phase'
        end_phase_button.onclick(self.set_destination_phase)

    def add_unit(self, x, y):
        # scale x and y values down from canvas:
        x /= self.scale
        y /= self.scale

        # Create query api:
        payload = {'x': x, 'y': y}
        response = self.query_api('units', 'post', payload=payload)

        # Print error, if it exists:
        coordinate = response.get('coordinate')
        if coordinate:
            print(f"unit added at {response['coordinate']}")
        # Otherwise, adding unit was successful:
        else:
            print(f"{response}")

        # Redraw all turtles:
        self.draw_all_units()

        # Finish by snapping the 'add_unit_turtle' back to its original position:
        add_unit_turtle = self.turtle_namespace.get('add_unit_phase_turtles')[-1]
        self.draw_add_unit_turtle(text="", add_unit_turtle=add_unit_turtle)

    def set_destination_phase(self, _x, _y):
        # _x and _y are required since 'onclick' calles this function with an x and y coordinate
        # (7A) control is received from 'add_unit_phase'
        # Start by cleaning up 'add_unit_phase_turtles':
        self.hide_turtles('add_unit_phase_turtles')

        # Bind drag-drog functions for setting destinations:
        destination_turtles = self.turtle_namespace.get('destination_turtles')
        for turtle in destination_turtles:
            turtle.onclick(...) # Draw the maximum movement distance around the associated unit
            turtle.ondrag(...) # Move the turtle to the cursor, placing it on the edge if it moves too far
            turtle.onrelease(...) # Place the unit destination at that position, attempting an API call

        # Create a 'run_turn' button, bind the API call:
        ...


    def add_target_phase(self):
        pass

if __name__ == "__main__":
    # Setup arguments:
    parser = ArgumentParser(
            description="A client written with Python's turtle for the Artillery game.")
    parser.add_argument("--url", type=str, required=True)
    args = parser.parse_args()
    url = args.url

    # Create game, main loop:
    game = Game(url)
    game.run()

