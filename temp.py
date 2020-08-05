#!/usr/bin/env python3

import os
import json
import subprocess

def execute_process(cmd, env_vars={}, fail_on_non_zero_exit=True, log_cmd=True, log_envvars=False, log_stdout=True, log_stderr=True):
    proc_env_vars = os.environ.copy()
    proc_env_vars = {**proc_env_vars, **env_vars}
    if log_cmd:
        print(f'Running {cmd}')
    if log_envvars:
        print('envvars')
        print(proc_env_vars)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=proc_env_vars)
    process.wait()
    out = []
    for item in process.stdout:
        item_formatted = item.decode().replace('\n', '')
        out.append(item_formatted)
    for item in out:
        if log_stdout:
            print(item)

    if process.returncode != 0:
        print(f'Process exited with return code {process.returncode}')
        print(process.stderr.read())
        if fail_on_non_zero_exit:
            raise ValueError('exiting')
    return out

def get_vars(vars_dict, vars_list, required=True):
    for var_item in vars_list:
        var_env_name = f'PLUGIN_{var_item}'.upper()
        var_env_value = os.getenv(var_env_name, None)
        if not var_env_value and required:
            raise ValueError('required variable {var_item} not found')
        vars_dict[var_item] = var_env_value

vars = {}
get_vars(vars, ['repo'])
get_vars(vars, ['tags', 'build_args', 'build_args_from_env', 'registry'], required=False)

can_push = False
registry = None
registry_is_ecr = False
registry_config_str = ''
cmd_env = {}
replica_str = ''
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

if can_push and '.ecr.' in registry and '.amazonaws.com' in registry:
    registry_is_ecr = True
    cmd_env['AWS_SDK_LOAD_CONFIG'] = 'true'
registry_param = ''
if can_push:
    registry_param = f'--push {registry} '

if can_push and registry_is_ecr:
    registry_config = {
        registry: {
            f'{repo}/*': {
                'push_chunk': -1,
                'security': {
                    'credsStore': 'ecr-login'
                }
            }
        }
    }
    registry_config_str = f'--registry-config=\'{json.dumps(registry_config)}\' '

for tag in vars['tags_list']:
    full_name = repo + ':' + tag
    cmd_line = f'/makisu-internal/makisu build --log-fmt console {registry_param}{registry_config_str}{replica_str}-t {full_name} .'
    execute_process(cmd_line, env_vars=cmd_env)

