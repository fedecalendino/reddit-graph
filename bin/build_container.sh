export DOCKER_DEFAULT_PLATFORM=linux/amd64

poetry export --without-hashes --format requirements.txt -o requirements.txt

docker build -t fedecalendino/reddit-graph .
