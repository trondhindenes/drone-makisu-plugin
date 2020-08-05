# Drone-Makisu plugin

Executes container builds in Drone CI using Makisu

Attempts to mimic the arguments for the regular docker plugin as closely as possible, 
including support for a `.tags` file which will be used if no tags are specified in settings.

## Things to know
### AWS ECR
this plugin tries to be smart about pushing to AWS ECR registries. If the registry hostname looks like an AWS ECR one, it automatically tries to set up the necessary auth settings. All you need to do is to use environment variables to specify AWS credentials, if the build isn't running with a role that has implicit access to AWS.

### Pusing to other registries
Not implemented just yet - coming shortly!

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
    path: /makisu-storage
  settings:
    storage: /cache
    repo: buildtest
    registry: 123.dkr.ecr.eu-west-1.amazonaws.com
```