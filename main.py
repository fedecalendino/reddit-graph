import django

django.setup()

from app import fetch

subreddit = fetch.subreddit("hearthstone")
print(subreddit.name)
print(subreddit.subscribers)
print(subreddit.type)
print(subreddit.created_at)

print(fetch.relations(subreddit))
