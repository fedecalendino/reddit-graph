import unittest
from app.jobs import main
from app.models.subreddit import Subreddit


class TestFetchSubreddit(unittest.TestCase):
    def test_public_subreddit(self):
        subreddit: Subreddit = main.fetch_subreddit("hearthstone")

        self.assertEqual(subreddit.name, "hearthstone")
        self.assertEqual(subreddit.color, "#7e53c1")
        self.assertEqual(
            subreddit.description,
            "For fans of Blizzard Entertainment's digital card game, Hearthstone",
        )
        self.assertEqual(
            subreddit.img_banner,
            "https://styles.redditmedia.com/t5_2w31t/styles/bannerBackgroundImage_b8u81y6zqyf91.jpg?width=4000&s=801ca9978ac6097952bfd45a576df59f36b052b5",
        )
        self.assertEqual(
            subreddit.img_header,
            "https://b.thumbs.redditmedia.com/aCDxJ4qjB4-_LPOT9OOKoRyIG-1mxbduvG_0lsCzBPA.png",
        )
        self.assertEqual(
            subreddit.img_icon,
            "https://b.thumbs.redditmedia.com/kOJ2mLk2e2e2kOto6K188zsLQzJE6Yv3AMi3Pv6kwkM.png",
        )
        self.assertEqual(subreddit.id, "2w31t")
        self.assertFalse(subreddit.nsfw)
        self.assertFalse(subreddit.quarantined)
        self.assertGreater(subreddit.subscribers, 1800000)
        self.assertEqual(subreddit.title, "Hearthstone")
        self.assertEqual(subreddit.type, "public")
        self.assertEqual(subreddit.url, "https://reddit.com/r/hearthstone")
        self.assertEqual(str(subreddit.created_at), "2013-01-17 18:33:00+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_nsfw(self):
        subreddit: Subreddit = main.fetch_subreddit("nsfw")

        self.assertEqual(subreddit.name, "nsfw")
        self.assertEqual(subreddit.color, "")
        self.assertEqual(subreddit.img_banner, "")
        self.assertEqual(
            subreddit.img_header,
            "https://b.thumbs.redditmedia.com/h5RmvyztneDLOkM1.png",
        )
        self.assertEqual(subreddit.img_icon, "")
        self.assertEqual(subreddit.id, "vf2")
        self.assertTrue(subreddit.nsfw)
        self.assertFalse(subreddit.quarantined)
        self.assertGreater(subreddit.subscribers, 3500000)
        self.assertEqual(subreddit.title, "Not Safe for Work")
        self.assertEqual(subreddit.type, "public")
        self.assertEqual(subreddit.url, "https://reddit.com/r/nsfw")
        self.assertEqual(str(subreddit.created_at), "2006-01-19 19:49:21+00:00")
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_private(self):
        subreddit: Subreddit = main.fetch_subreddit("ravenclaw")

        self.assertEqual(subreddit.name, "ravenclaw")
        self.assertEqual(subreddit.color, None)
        self.assertEqual(subreddit.img_banner, None)
        self.assertEqual(subreddit.img_header, None)
        self.assertEqual(subreddit.img_icon, None)
        self.assertEqual(subreddit.id, None)
        self.assertEqual(subreddit.nsfw, None)
        self.assertEqual(subreddit.quarantined, None)
        self.assertEqual(subreddit.subscribers, None)
        self.assertEqual(subreddit.title, None)
        self.assertEqual(subreddit.type, "private")
        self.assertEqual(subreddit.url, "https://reddit.com/r/ravenclaw")
        self.assertEqual(str(subreddit.created_at), None)
        self.assertIsNotNone(subreddit.updated_at)

    def test_public_subreddit_banned(self):
        subreddit: Subreddit = main.fetch_subreddit("bitcoin_price")

        self.assertEqual(subreddit.name, "bitcoin_price")
        self.assertEqual(subreddit.color, None)
        self.assertEqual(subreddit.img_banner, None)
        self.assertEqual(subreddit.img_header, None)
        self.assertEqual(subreddit.img_icon, None)
        self.assertEqual(subreddit.id, None)
        self.assertEqual(subreddit.nsfw, None)
        self.assertEqual(subreddit.quarantined, None)
        self.assertEqual(subreddit.subscribers, None)
        self.assertEqual(subreddit.title, None)
        self.assertEqual(subreddit.type, "banned")
        self.assertEqual(subreddit.url, "https://reddit.com/r/bitcoin_price")
        self.assertEqual(str(subreddit.created_at), None)
        self.assertIsNotNone(subreddit.updated_at)
