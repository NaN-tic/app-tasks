#This file is part of tryton-task. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import logging
import sys
from invoke import Collection

# import here your tryton tasks projects
from .app import AppCollection

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

ns = Collection()
ns.add_collection(AppCollection, 'app')
