docker build -t trondhindenes/drone-makisu-plugin .
docker push trondhindenes/drone-makisu-plugin

docker run --rm \
  -e PLUGIN_REPO=hello \
  -e PLUGIN_TAGS=what \
  trondhindenes/drone-makisu-plugin