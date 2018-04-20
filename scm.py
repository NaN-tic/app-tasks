#This file is part of trytontasks_scm. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import hgapi
import logging
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