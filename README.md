# Drone-Makisu plugin

Executes container builds in Drone CI using Makisu

Attempts to mimic the arguments for the regular docker plugin as closely as possible, 
including support for a `.tags` file which will be used if no tags are specified in settings.

## Things to know
### AWS ECR
this plugin tries to be smart about pushing to AWS ECR registries. If the registry hostname looks like an AWS ECR one, it automatically tries to set up the necessary auth settings. All you need to do is to use environment variables to specify AWS credentials, if the build isn't running with a role that has implicit access to AWS.

### Pusing to other registries
Not implemented just yet - coming shortly!

## Parameters
repo: required. Given the image name `trondhindenes/drone-makisu-plugin:latest`, the `repo` field would be `drone-makisu-plugin`. If this parameter is specified as `xx/xx` and `registry` isnt specified, the field will be automatically split into registry and repo.
tags: optional. List of tags to use on the image. Defaults to 'latest'.  If this parameter is omitted, and a file called `.tags` is found in the local dir, that file will be used instead. It should contain a comma-separated list of tags to use.
build_args: optional. Dict of build args to use when building the image
build_args_from_env: optional. List of env vars to convert to build args
registry: optional. where to push the image. See also `repo` above
dockerfile: optional, defaults to `Dockerfile`
debug: optional. Set it to `true` to print more info
storage: optional. specify cache dir for layers
commit: optional. Defaults to `implicit`. Set it to `explicit` to use makisu's smart caching feature.

## Example
```yaml
---
kind: pipeline
type: kubernetes
name: default

volumes:
- name: cache
  temp: {}

steps:
- name: makisu1
  image: trondhindenes/drone-makisu-plugin
  pull: always
  environment:
    country: au
    country: jazz
  volumes:
  - name: cache
    path: /cache
  settings:
    storage: /cache
    repo: buildtest
    registry: 123.dkr.ecr.eu-west-1.amazonaws.com
    build_args:
      WHAT: 'hello'
      SUM: 'oof'
    build_args_from_env:
    - country
    - music

- name: makisu2
  image: trondhindenes/drone-makisu-plugin
  pull: always
  volumes:
  - name: cache
    path: /cache
  settings:
    storage: /cache
    repo: buildtest
    registry: 123.dkr.ecr.eu-west-1.amazonaws.com
    tags:
    - latest
    - what
```