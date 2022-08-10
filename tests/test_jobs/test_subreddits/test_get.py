import unittest
from app.jobs import subreddits
from app.models.subreddit import Subreddit, SubredditType


class TestSubredditsGet(unittest.TestCase):
    def test_public_subreddit(self):
        subreddit: Subreddit = subreddits.get("hearthstone")

        self.assertEqual(subreddit.name, "hearthstone")
        self.assertEqual(subreddit.color, "#7e53c1")
        self.assertEqual(
            subreddit.description,
            "For fans of Blizzard Entertainment's digital card game, Hearthstone",
        )
        self.assertEqual(subreddit.id, "2w31t")
        self.assertFalse(subreddit.nsfw)
        self.assertFalse(subreddit.quarantined)
        self.assertGreater(subreddit.subscribers, 1800000)
        self.assertEqual(subreddit.title, "Hearthstone")
        self.assertEqual(subreddit.type, SubredditType.PUBLIC)
        self.assertEqual(subreddit.url, "https://reddit.com/r/hearthstone")
        self.assertEqual(str(subreddit.created_at), "2013-01-17 18:33:00+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_nsfw(self):
        subreddit: Subreddit = subreddits.get("nsfw")

        self.assertEqual(subreddit.name, "nsfw")
        self.assertEqual(subreddit.color, "")
        self.assertEqual(subreddit.id, "vf2")
        self.assertTrue(subreddit.nsfw)
        self.assertFalse(subreddit.quarantined)
        self.assertGreater(subreddit.subscribers, 3500000)
        self.assertEqual(subreddit.title, "Not Safe for Work")
        self.assertEqual(subreddit.type, SubredditType.PUBLIC)
        self.assertEqual(subreddit.url, "https://reddit.com/r/nsfw")
        self.assertEqual(str(subreddit.created_at), "2006-01-19 19:49:21+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_private(self):
        subreddit: Subreddit = subreddits.get("ravenclaw")

        self.assertEqual(subreddit.name, "ravenclaw")
        self.assertIsNone(subreddit.color)
        self.assertEqual(subreddit.id, "2sjxt")
        self.assertIsNone(subreddit.img_banner)
        self.assertIsNone(subreddit.img_header)
        self.assertIsNone(subreddit.img_icon)
        self.assertIsNone(subreddit.nsfw)
        self.assertIsNone(subreddit.quarantined)
        self.assertIsNone(subreddit.subscribers)
        self.assertEqual(subreddit.title, "Ravenclaw Tower")
        self.assertEqual(subreddit.type, SubredditType.PRIVATE)
        self.assertEqual(subreddit.url, "https://reddit.com/r/ravenclaw")
        self.assertEqual(str(subreddit.created_at), "2011-06-10 21:12:36+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_banned(self):
        subreddit: Subreddit = subreddits.get("bitcoin_price")

        self.assertEqual(subreddit.name, "bitcoin_price")
        self.assertIsNone(subreddit.color)
        self.assertEqual(subreddit.id, "3771f")
        self.assertIsNone(subreddit.img_banner)
        self.assertIsNone(subreddit.img_header)
        self.assertIsNone(subreddit.img_icon)
        self.assertIsNone(subreddit.nsfw)
        self.assertIsNone(subreddit.quarantined)
        self.assertIsNone(subreddit.subscribers)
        self.assertEqual(subreddit.title, "To The Moon ..○")
        self.assertEqual(subreddit.type, SubredditType.BANNED)
        self.assertEqual(subreddit.url, "https://reddit.com/r/bitcoin_price")
        self.assertEqual(str(subreddit.created_at), "2015-02-26 16:50:49+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_non_existent(self):
        subreddit: Subreddit = subreddits.get("this_doesnt_exist")

        self.assertEqual(subreddit.name, "this_doesnt_exist")
        self.assertIsNone(subreddit.color)
        self.assertIsNone(subreddit.id)
        self.assertIsNone(subreddit.img_banner)
        self.assertIsNone(subreddit.img_header)
        self.assertIsNone(subreddit.img_icon)
        self.assertIsNone(subreddit.nsfw)
        self.assertIsNone(subreddit.quarantined)
        self.assertIsNone(subreddit.subscribers)
        self.assertIsNone(subreddit.title)
        self.assertEqual(subreddit.type, SubredditType.NON_EXISTENT)
        self.assertEqual(subreddit.url, "https://reddit.com/r/this_doesnt_exist")
        self.assertIsNone(subreddit.created_at)
        self.assertIsNotNone(subreddit.updated_at)
