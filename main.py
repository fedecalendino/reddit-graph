import django

django.setup()

from app import crawler

subreddit = crawler.fetch_random_subreddit()
print(subreddit.name)
print(subreddit.subscribers)
print(subreddit.type)
print(subreddit.created_at)

print("sidebar")
list(map(lambda name: print("", "*", name), crawler.fetch_sidebar_relations(subreddit)))

print("wiki")
list(map(lambda name: print("", "*", name), crawler.fetch_wiki_relations(subreddit)))
