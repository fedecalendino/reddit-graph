export DOCKER_DEFAULT_PLATFORM=linux/amd64

poetry export --without-hashes --format requirements.txt -o requirements.txt

docker build -t fedecalendino/reddit-graph .

docker push fedecalendino/reddit-graph

az webapp log tail --name redditgraph-app --resource-group reddit-graph
