poetry export --without-hashes --format requirements.txt -o requirements.txt

docker build -t fedecalendino/reddit-graph .
