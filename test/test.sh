docker build -t drone-makisu .

docker run --rm -it \
    -v ${PWD}:/work \
    -w /work \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -e PLUGIN_IMAGE_TAG=mytesttag \
    -e PLUGIN_DOCKERFILE=test/Dockerfile_test \
    drone-makisu \
