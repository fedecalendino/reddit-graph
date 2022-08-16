import unittest

from app import helpers
from app.constants import EXCLUDED


class TestFindSubreddits(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(helpers.validate_subreddit_name("hearthstone"))
        self.assertTrue(helpers.validate_subreddit_name("wow"))

    def test_invalid(self):
        self.assertFalse(helpers.validate_subreddit_name("a"))
        self.assertFalse(helpers.validate_subreddit_name("thisnameiswaaaaaytoolong"))

    def test_excluded(self):
        for excluded in EXCLUDED:
            self.assertFalse(helpers.validate_subreddit_name(excluded))
