import json

import django
from prawcore.exceptions import NotFound, Forbidden, Redirect

django.setup()


from app.reddit import reddit

for sub in ["hearthstone", "genzedong", "ravenclaw", "the_donald", "uye2038ry3"]:
    try:
        subreddit = reddit.subreddit(sub)

        if subreddit.quarantine:
            subreddit.quaran.opt_in()

        print("id", subreddit.id)
        print("name", subreddit.display_name.lower())
        print("nsfw", subreddit.over18)
        print("created at", subreddit.created_utc)
        print("color", subreddit.key_color)
        print("icon", subreddit.icon_img)
        print("title", subreddit.title)
        print("quarantine", subreddit.quarantine)
        print("subscribers", subreddit.subscribers)
        print("type", subreddit.subreddit_type)
        print("wiki", subreddit.wiki_enabled)
        print("-" * 10)
    except Forbidden as exc:
        response = json.loads(exc.response.text)
        print(sub, response["reason"])
    except NotFound as exc:
        response = json.loads(exc.response.text)
        print(sub, response["reason"])
    except Redirect as exc:
        print(sub, "unexistent")
