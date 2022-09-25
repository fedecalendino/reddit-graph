./build_container.sh

docker push fedecalendino/reddit-graph

az webapp log tail --name redditgraph-app --resource-group reddit-graph
