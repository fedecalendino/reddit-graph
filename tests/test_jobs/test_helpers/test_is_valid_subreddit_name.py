import unittest
from app.jobs import helpers
from app.constants import EXCLUDED


class TestFindSubreddits(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(helpers.is_valid_subreddit_name("hearthstone"))
        self.assertTrue(helpers.is_valid_subreddit_name("wow"))

    def test_invalid(self):
        self.assertFalse(helpers.is_valid_subreddit_name("a"))
        self.assertFalse(helpers.is_valid_subreddit_name("thisnameiswaaaaaytoolong"))

    def test_excluded(self):
        for excluded in EXCLUDED:
            self.assertFalse(helpers.is_valid_subreddit_name(excluded))
