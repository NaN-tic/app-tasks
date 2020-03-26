#This file is part of trytontasks_scm. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import hgapi
import git
import os
import sys
import logging
from invoke import run
from blessings import Terminal

t = Terminal()
logger = logging.getLogger(__name__)

def check_revision(client, module, revision, branch):
    if client.revision(revision).branch != branch:
        logger.info(t.bold_red('[' + module + ']'))
        logger.info("Invalid revision '%s': it isn't in branch '%s'"
            % (revision, branch))
        return -1
    return 0

def hg_clone(url, path, branch="default", revision=None):
    extended_args = ['--pull']
    if revision or branch:
        extended_args.append('-u')
        extended_args.append(revision or branch)
    try:
        client = hgapi.hg_clone(url, path, *extended_args)
        if revision:
            check_revision(client, path, revision, branch)
    except hgapi.HgException, e:
        logger.info(t.bold_red('[' + path + ']'))
        logger.info("Error running %s: %s" % (e.exit_code, str(e)))
        return -1
    except:
        return -1

    if revision:
        logger.info("Repo " + t.bold(path) + t.green(" Updated") + \
            " to revision: " + revision)
    else:
        logger.info("Repo " + t.bold(path) + t.green(" Updated") + \
            " and branch: " + branch)

def hg_update(path):
    try:
        repo = hgapi.Repo(path)
        repo.hg_pull()
        revision = repo.hg_branch()
        repo.hg_update(revision)
    except hgapi.HgException, e:
        logger.info(t.bold_red('[' + path + ']'))
        logger.info("Error running %s: %s" % (e.exit_code, str(e)))
        return -1
    except:
        return -1

    logger.info("Repo " + t.bold(path) + t.green(" Updated"))

def git_clone(url, path, branch="master", revision="master"):
    git.Repo.clone_from(url, path, branch=branch)
    print("Repo " + t.bold(path) + t.green(" Cloned"))
    return 0

def git_pull(module, path, update=False, clean=False, branch=None,
        revision=None, ignore_missing=False):
    """
    Params update, clean, branch and revision are not used.
    """
    path_repo = os.path.join(path, module)
    if not os.path.exists(path_repo):
        if ignore_missing:
            return 0
        print(sys.stderr, t.red("Missing repositori:") + t.bold(path_repo))
        return -1

    cwd = os.getcwd()
    os.chdir(path_repo)

    cmd = ['git', 'pull']
    result = run(' '.join(cmd), warn=True, hide='both')

    if not result.ok:
        print(sys.stderr, t.red("= " + module + " = KO!"))
        print(sys.stderr, result.stderr)
        os.chdir(cwd)
        return -1

    # If git outputs 'Already up-to-date' do not print anything.
    if 'Already up-to-date' in result.stdout:
        os.chdir(cwd)
        return 0

    print(t.bold("= " + module + " ="))
    print(result.stdout)
    os.chdir(cwd)
    return 0
