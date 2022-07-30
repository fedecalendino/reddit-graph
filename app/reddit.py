from django.conf import settings
from praw import Reddit


reddit = Reddit(
    client_id=settings.REDDIT["CLIENT_ID"],
    client_secret=settings.REDDIT["CLIENT_SECRET"],
    user_agent=settings.REDDIT["USERAGENT"],
    username=settings.REDDIT["USERNAME"],
    password=settings.REDDIT["PASSWORD"],
)

assert reddit.user.me().name == settings.REDDIT["USERNAME"]
