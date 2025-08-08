import requests
import argparse
from turtle import Turtle

# Globals
URL = None

class Unit:
    def __init__(self, x, y):
        self.pos = (x, y)
        self.des = (x, y)
        self.t = Turtle()
        self.t.color('blue')


class Target:
    def __init__(self, x, y, cost):
        self.pos = (x, y)
        self.cost = cost
        self.t = Turtle()
        self.t.color('red')


class Game:
    def __init__(self):
        self.units = []
        self.targets = []
        self.map_radius = 0

    def run(self):
        # Draw the map:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='A client written with Python\'s turtle for the Artillery game.')
    parser.add_argument('--url', type=str, required=True)
    args = parser.parse_args()
    URL = args.url
    game = Game()
    while True:
        try:
            game.run()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
    print(requests.get(f"{URL}/units").json())
