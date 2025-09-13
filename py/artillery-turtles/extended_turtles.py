"""**extended_turtles** is a collection of classes which extend the functionality of Python's `turtle.Turtle` class.
"""
from turtle import Turtle

class ButtonTurtle(Turtle):
    """Provides `onclick` functionality to a turtle."""
    def onclick(self, onclick_callback, onclick_side_effects):
        super().onclick(onclick_callback)
        self.onclick_side_effects = onclick_side_effects


class UnitTurtle(Turtle):
    ...


class DestinationTurtle(Turtle):
    ...


class TargetTurtle(Turtle):
    ...


class ShapeTurtle(Turtle):
    ...
