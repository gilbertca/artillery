from unittest import TestCase

from ...main import main

class MainTests(TestCase):
    """MainTests contains all tests for the `main` module."""
    def test_max_retries(self):
        main()
