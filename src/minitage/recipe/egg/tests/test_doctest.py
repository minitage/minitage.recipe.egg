__docformat__ = 'restructuredtext'

import unittest2 as unittest
import glob
import logging
import doctest
import os

from minitage.recipe.egg.testing import LAYER as layer
from plone.testing import layered

J = os.path.join
D = os.path.dirname

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)
import pkg_resources
cwd = pkg_resources.resource_filename(
    'minitage.recipe.egg', 'tests')
root = D(D(D(D(D(cwd)))))


def test_suite():
    """This must be runned from buildout !"""
    logger = logging.getLogger('minitage.recipe.egg.tests')
    cwd = os.path.dirname(__file__)
    files = []
    try:
        files = []
        for e in ['*rst', '*txt']:
            for d in [cwd,
                      os.path.dirname(cwd)]:
                files += glob.glob(os.path.join(d, e))
    except Exception, e:
        logger.warn('No doctests for minitage.recipe.egg')
    suite = unittest.TestSuite()
    globs = globals()
    for s in files:
        suite.addTests([
            layered(
                doctest.DocFileSuite(
                    s,
                    globs=globs,
                    module_relative=False,
                    optionflags=optionflags,
                ),
                layer=layer
            ),
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
