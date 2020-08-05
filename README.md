# Drone-Makisu plugin

Executes container builds in Drone CI using Makisu

Attemps to mimic the arguments for the regular docker plugin as closely as possible, 
including support for a `.tags` file which will be used if no tags are specified in settings.

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
    path: /makisu-storage
  settings:
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
    repo: buildtest
    registry: 123.dkr.ecr.eu-west-1.amazonaws.com
```