import json
import re

import django
from prawcore.exceptions import NotFound, Forbidden, Redirect

django.setup()

SUBREDDIT_REGEX = r"""/r/(\w*).*"""


from app.reddit import reddit

for sub in ["koreanvariety"] + ["random"] * 10 + ["randnsfw"] * 5:
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

        print("topbar")
        topbar_subreddits = set()

        for widget in subreddit.widgets.topbar:
            if widget.kind != "menu":
                continue

            items = []

            for data in widget.data:
                if hasattr(data, "children"):
                    items.extend(data.children)
                else:
                    items.append(data)

            for item in items:
                topbar_subreddits.update(
                    set(
                        map(
                            lambda found: found.lower(),
                            re.findall(
                                SUBREDDIT_REGEX,
                                str(item.url),
                                flags=re.IGNORECASE,
                            ),
                        )
                    )
                )

        list(map(lambda name: print("*", name), topbar_subreddits))

        print("sidebar")
        sidebar_subreddits = set()

        for widget in subreddit.widgets.sidebar:
            if widget.kind != "community-list":
                continue

            sidebar_subreddits.update(
                set(
                    map(
                        lambda found: found.display_name.lower(),
                        widget.data,
                    )
                )
            )

        list(map(lambda name: print("*", name), sidebar_subreddits))

        print("wiki")
        wiki_subreddits = set()

        for index, wiki in enumerate(subreddit.wiki):
            print("-", "page:", index)

            wiki_subreddits.update(
                set(
                    map(
                        lambda found: found.lower(),
                        re.findall(
                            SUBREDDIT_REGEX,
                            str(wiki.content_html),
                            flags=re.IGNORECASE,
                        ),
                    )
                )
            )

        list(map(lambda name: print("", "*", name), wiki_subreddits))

        print("-" * 10)
    except Forbidden as exc:
        response = json.loads(exc.response.text)
        print(sub, response["reason"])
    except NotFound as exc:
        response = json.loads(exc.response.text)
        print(sub, response["reason"])
    except Redirect as exc:
        print(sub, "unexistent")
