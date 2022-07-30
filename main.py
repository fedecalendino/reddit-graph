import django
from prawcore.exceptions import NotFound, Forbidden, Redirect

django.setup()


from app.reddit import reddit

for sub in [
    "ravenclaw",
    "call",
    "random",
]:
    try:
        subreddit = reddit.subreddit(sub)
        print(subreddit.id)
        print(subreddit.display_name.lower())
        print(subreddit.over18)
        print(subreddit.created_utc)
        print(subreddit.key_color)
        print(subreddit.quarantine)
        print(subreddit.subscribers)
        print(subreddit.subreddit_type)
        print(subreddit.wiki_enabled)
        print()
    except Forbidden:
        print(sub, "private")
    except NotFound:
        print(sub, "banned")
    except Redirect:
        print(sub, "unexistent")
