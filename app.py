#This file is part of tryton-task. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from configparser import ConfigParser
import logging
import os
import hgapi
from invoke import Collection, task
from blessings import Terminal
from .scm import hg_clone, hg_update, git_clone, git_pull


t = Terminal()
logger = logging.getLogger(__name__)

__all__ = ['info', 'clone', 'branches']


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"

def read_config_file():
    'Read config file'
    Config = ConfigParser()
    Config.readfp(open('./local.cfg'))
    return Config

@task
def info(ctx):
    'Info config modules'
    Config = read_config_file()
    modules = Config.sections()
    modules.sort()

    total = len(modules)
    logger.info(t.bold(str(total) + ' modules'))

    for module in modules:
        message = t.green(module)+' %s %s %s %s' % (
            Config.get(module, 'repo'),
            Config.get(module, 'url'),
            Config.get(module, 'path'),
            Config.get(module, 'branch'),
            )
        print(message)

def _hg_branches(module, path, config_branch=None):
    client = hgapi.Repo(path)
    branches = client.get_branch_names()
    active = client.hg_branch()

    b = []
    branches.sort()
    branches.reverse()
    for branch in branches:
        br = branch

        if branch == active:
            br = "*" + br

        if branch == config_branch:
            br = "[" + br + "]"

        b.append(br)

    msg = str.ljust(module, 40, ' ') + "\t".join(b)

    if "[*" in msg:
        msg = bcolors.OKGREEN + msg + bcolors.ENDC
    elif "\t[" in msg or '\t*' in msg:
        msg = bcolors.FAIL + msg + bcolors.ENDC
    else:
        msg = bcolors.WARN + msg + bcolors.ENDC

    logger.info(msg)

@task(help={
    'branch': 'Repo branch. Default is "default"',
    })
def clone(ctx, branch=None):
    '''Clone trytond modules'''
    Modules = read_config_file()

    modules = Modules.sections()
    modules.sort()

    for module in modules:
        repo = Modules.get(module, 'repo')
        url = Modules.get(module, 'url')
        path = Modules.get(module, 'path')
        mod_branch = branch or Modules.get(module, 'branch')

        repo_path = os.path.join(path, module)
        if os.path.exists(repo_path):
            continue

        logger.info( "App " + t.bold(module) + " to clone")
        if repo == 'hg':
            hg_clone(url, repo_path, mod_branch)
        else:
            git_clone(url, repo_path, mod_branch)

@task
def update(ctx, module=None):
    '''Update trytond modules'''
    Modules = read_config_file()

    modules = Modules.sections()
    modules.sort()

    if module:
        if module in modules:
            modules = [module]
        else:
            logger.error( "Not found " + t.bold(module))
            return

    for module in modules:
        repo = Modules.get(module, 'repo')
        path = Modules.get(module, 'path')
        branch = Modules.get(module, 'branch')

        repo_path = os.path.join(path, module)
        if not os.path.exists(repo_path):
            continue

        logger.info( "APP " + t.bold(module) + " to update")
        if repo == 'hg':
            hg_update(repo_path)
        else:
            git_pull(repo_path, '.', True, branch=branch)

@task
def branches(ctx, module=None):
    '''Show info module branches'''
    Modules = read_config_file()

    modules = Modules.sections()
    modules.sort()

    if module:
        modules = [module] if (module and module in modules) else None

    for module in modules:
        repo = Modules.get(module, 'repo')
        url = Modules.get(module, 'url')
        path = Modules.get(module, 'path')
        branch = Modules.get(module, 'branch')

        repo_path = os.path.join(path, module)

        if repo == 'hg':
            _hg_branches(module, repo_path, branch)
        else:
            logger.info('Not available branches option with %s' % repo)
            return

# Add Invoke Collections
AppCollection = Collection()
AppCollection.add_task(info)
AppCollection.add_task(clone)
AppCollection.add_task(update)
AppCollection.add_task(branches)
