import unittest

from app import helpers


class TestFindSubreddits(unittest.TestCase):
    def test_valid(self):
        text = "/r/hearthstone /r/wow"
        result = helpers.find_subreddits(text)

        self.assertSetEqual(
            {"hearthstone", "wow"},
            set(result),
        )

    def test_invalid(self):
        text = "/r/a /r/correctlength r/missingfirstslash /r/thisnameiswaytoolongbutshouldbeook"
        result = helpers.find_subreddits(text)

        self.assertSetEqual(
            {"correctlength", "thisnameiswaytoolongbutshouldbeook"},
            set(result),
        )
