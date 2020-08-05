#!/usr/bin/env python3

import os
import json
import subprocess
import time
import sys

def execute_process(cmd, env_vars={}, fail_on_non_zero_exit=True, log_cmd=True, log_envvars=False, log_stdout=True, log_stderr=True):
    proc_env_vars = os.environ.copy()
    proc_env_vars = {**proc_env_vars, **env_vars}
    if log_cmd:
        print(f'Running {cmd}')
    if log_envvars:
        print('envvars')
        print(proc_env_vars)
    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, env=proc_env_vars)
    return_code = None
    while True:
        return_code = process.poll()
        if return_code is not None:
            break
        else:
            time.sleep(0.05)
    if return_code != 0:
        print(f'Process exited with return code {return_code}')
        if fail_on_non_zero_exit:
            raise ValueError('exiting')
    return

def get_vars(vars_dict, vars_list, required=True):
    for var_item in vars_list:
        var_env_name = f'PLUGIN_{var_item}'.upper()
        var_env_value = os.getenv(var_env_name, None)
        if not var_env_value and required:
            raise ValueError('required variable {var_item} not found')
        vars_dict[var_item] = var_env_value

vars = {}
get_vars(vars, ['repo'])
get_vars(vars, ['tags', 'build_args', 'build_args_from_env', 'registry', 'dockerfile', 'debug', 'storage', 'commit'], required=False)

debug = False
if vars['debug'] and vars['debug'].lower() == 'true':
    debug = True

commit = 'implicit'
if vars['commit'] and vars['commit'] == 'explicit':
    commit = 'explicit'

storage_str = ''
if vars['storage']:
    storage_str = '--storage=' + vars['storage'] + ' '

if not vars['dockerfile']:
    vars['dockerfile'] = 'Dockerfile'

dockerfile = vars['dockerfile']

if not vars['tags'] and os.path.exists('.tags'):
    with open('.tags', 'r') as stream:
        tags_from_files = stream.read()
        vars['tags'] = tags_from_files.replace(os.linesep, '')
    print('read tags from .tags file:')
    print(vars['tags'])

if debug:
    print(json.dumps(vars, indent=4, sort_keys=True))

can_push = False
registry = None
registry_is_ecr = False
registry_config_str = ''
cmd_env = {}
replica_str = ''
build_args_str = ''

if vars['build_args']:
    build_args = json.loads(vars['build_args'])
    for build_arg in build_args.keys():
        build_arg_value = build_args[build_arg]
        arg_str = f'--build-arg {build_arg}={build_arg_value} '
        build_args_str += arg_str

if vars['build_args_from_env']:
    build_args_from_env = vars['build_args_from_env'].split(',')
    for build_arg in build_args_from_env:
        build_arg_value = os.getenv(build_arg)
        arg_str = f'--build-arg {build_arg}={build_arg_value} '
        build_args_str += arg_str

if '/' in vars['repo'] and not vars['registry']:
    registry = vars['repo'].split('/')[0]
    repo = vars['repo'].split('/')[1]
    can_push = True
elif '/' in vars['repo'] and vars['registry']:
    registry = vars['registry']
    repo = vars['repo'].split('/')[1]
    can_push = True
elif vars['registry']:
    registry = vars['registry']
    repo = vars['repo']
    can_push = True
else:
    print('registry not specified, not able to push')
    repo = vars['repo']

if not vars['tags']:
    vars['tags'] = 'latest'
vars['tags_list'] = vars['tags'].split(',')
vars['tags_list'] = sorted(list(set(vars['tags_list'])))
first_tag = vars['tags_list'][0]

if can_push and len(vars['tags_list']) > 1:
    replica_pushes = []
    replica_str = ''
    for tag in vars['tags_list'][1:]:
        replica_str += f'--replica "{registry}/{repo}:{tag}" '
    replica_str = replica_str[:-1] + ' '

full_name_first_img = repo + ':' + first_tag

if can_push and '.ecr.' in registry and '.amazonaws.com' in registry:
    registry_is_ecr = True
    cmd_env['AWS_SDK_LOAD_CONFIG'] = 'true'


if can_push and registry_is_ecr:
    registry_config = {
        registry: {
            '.*': {
                'push_chunk': -1,
                'security': {
                    'credsStore': 'ecr-login'
                }
            }
        }
    }
    registry_config_str = f'--registry-config=\'{json.dumps(registry_config)}\' '

registry_param = ''
if can_push:
    registry_param = f'--push {registry} '

cmd_line = f'/makisu-internal/makisu build -t {full_name_first_img} --commit={commit} --modifyfs=true --log-fmt=console -f {dockerfile} {storage_str}{registry_param}{registry_config_str}{replica_str}{build_args_str} .'
execute_process(cmd_line, env_vars=cmd_env, log_cmd=debug)
