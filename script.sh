#!/bin/sh

set -e
export PLUGIN_DOCKERFILE="${PLUGIN_DOCKERFILE:-Dockerfile}"

/makisu-internal/makisu build -t=$PLUGIN_IMAGE_TAG -f $PLUGIN_DOCKERFILE .
