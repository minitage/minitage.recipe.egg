#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from plone.testing.layer import Layer as Base

from StringIO import StringIO
import shutil
import tempfile
import subprocess
import pkg_resources
import sys
import os

from setuptools.package_index import PackageIndex
#from zc.buildout.testing import *


from os import makedirs
from zc.buildout.buildout import Buildout
from zc.buildout import buildout as bo
from zc.buildout.testing import (
    start_server,
    remove,
    _start_server,
    stop_server,
)


from minitage.core.common import remove_path, which


D = os.path.dirname


def get_uname():
    if 'linux' in sys.platform:
        return 'linux'
    else:
        return sys.platform

uname = get_uname()


def get_args(args):
    res = []
    for arg in args:
        if isinstance(arg, str):
            res.append(arg)
        if isinstance(arg, list) or isinstance(arg, tuple):
            res.extend(get_args(arg))
    return res


def get_joined_args(args):
    res = get_args(args)
    return os.path.join(*res)


current_dir = os.path.abspath(os.path.dirname(__file__))


def mkdir(*args):
    a = get_joined_args(args)
    if not os.path.isdir(a):
        makedirs(a)


def rmdir(*args):
    a = get_joined_args(args)
    if os.path.isdir(a):
        shutil.rmtree(a)


def sh(cmd, in_data=None, out=None):
    if out is not None:
        if isinstance(out, bool):
            out = StringIO()
    _cmd = cmd
    if out is None:
        print cmd
    elif out:
        out.write(cmd)
    p = subprocess.Popen([_cmd], shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=True)

    if in_data is not None:
        p.stdin.write(in_data)

    p.stdin.close()

    if out is None:
        print p.stdout.read()
        print p.stderr.read()
    elif out:
        out.write(p.stdout.read())
        out.write(p.stderr.read())


def ls(*args):
    a = get_joined_args(args)
    if os.path.isdir(a):
        filenames = os.listdir(a)
        for filename in sorted(filenames):
            print filename
    else:
        print 'No directory named %s' % args


def cd(*args):
    a = get_joined_args(args)
    os.chdir(a)


def config(filename):
    return os.path.join(current_dir, filename)


def install(dist, destination):
    if isinstance(dist, str):
        dist = pkg_resources.working_set.find(
            pkg_resources.Requirement.parse(dist))
    if dist.location.endswith('.egg'):
        destination = os.path.join(destination,
                                   os.path.basename(dist.location),
                                   )
        if os.path.isdir(dist.location):
            shutil.copytree(dist.location, destination)
        else:
            shutil.copyfile(dist.location, destination)
    else:
        open(os.path.join(
            destination, dist.project_name + '.egg-link'), 'w'
        ).write(dist.location)


def install_develop(dist, destination):
    if not isinstance(destination, str):
        destination = os.path.join(destination.globs['sample_buildout'],
                                   'develop-eggs')
    if isinstance(dist, str):
        dist = pkg_resources.working_set.find(
            pkg_resources.Requirement.parse(dist))
    open(
        os.path.join(destination,
                     dist.project_name + '.egg-link'), 'w'
    ).write(dist.location)


def install_buildout(requirements, destination):
    develop_path = os.path.join(
        destination, 'develop-eggs')
    eggs_path = os.path.join(
        destination, 'eggs')
    for p in [eggs_path, develop_path]:
        if not os.path.exists(p):
            os.makedirs(p)
    if not isinstance(requirements, (list, tuple)):
        requirements = [requirements]
    env = pkg_resources.Environment()
    ws = pkg_resources.WorkingSet()
    rs = []
    for req in requirements:
        rs.append(pkg_resources.Requirement.parse(req))
    dists = ws.resolve(rs, env)
    todo = {}
    for dist in dists:
        todo.setdefault(dist.precedence, [])
        todo[dist.precedence].append(dist)
    for p in [pkg_resources.DEVELOP_DIST,
              pkg_resources.EGG_DIST]:
        for dist in todo.get(p, []):
            install(dist, eggs_path)


def cat(*args, **kwargs):
    filename = os.path.join(*args)
    if os.path.isfile(filename):
        data = open(filename).read()
        if kwargs.get('returndata', False):
            return data
        print data
    else:
        print 'No file named %s' % filename


def touch(*args, **kwargs):
    filename = os.path.join(*args)
    open(filename, 'w').write(kwargs.get('data', ''))


def clean():
    noecho = [remove(os.path.join('eggs', egg))
              for egg in os.listdir('eggs') if 'foo' in egg]


def cleandist():
    if os.path.exists('minitage/eggs'):
        noecho = [os.remove(os.path.join('minitage/eggs', d))
                  for d in os.listdir('minitage/eggs') if '.tar.gz' in d]
    if os.path.exists('eggs'):
        noecho = [os.remove(os.path.join('eggs', d))
                  for d in os.listdir('eggs') if '.tar.gz' in d]
    noecho = [os.remove(d)
              for d in os.listdir('.') if '.tar.gz' in d]

SETUP = """
from setuptools import setup
%s
setup(name='%s',
      version='%s',
      py_modules=['toto'])
"""
MODULE = """
def f():
    print "foo"
"""


def makedist(name="foo", version="1.0", module=MODULE, setup=''):
    touch('foo/setup.py',
          data=SETUP % (setup, name, version))
    touch('foo/toto.py', data=MODULE)
    os.chdir('foo')
    sh('python setup.py sdist', out=False)
    noecho = [shutil.copy(
        os.path.join('dist', d), os.path.join('..', d))
        for d in os.listdir('dist')]
    os.chdir('..')


def buildout(*args):
    argv = sys.argv[:]
    sys.argv = ["foo"] + list(args)
    ret = bo.main()
    sys.argv = argv
    return ret


def bootstrap():
    sh('buildout -o bootstrap', out=StringIO())


class Layer(Base):

    defaultBases = tuple()
    requirements = ('minitage.recipe.egg',)
    # Layer lifecycle methods - overriden by subclasses

    def setUp(self):
        tmp = tempfile.mkdtemp()
        root = self["p"] = self["tempdir"] = tmp
        bp = self["bp"] = os.path.join(
            tmp, 'root', 'categ', 'test')
        testd = os.path.join(bp, 'test')
        if not os.path.exists(root):
            os.makedirs(root)
        if not os.path.exists(testd):
            os.makedirs(testd)
        self['__tear_downs'] = __tear_downs = []
        self['register_teardown'] = __tear_downs.append

        def start_index(path):
            port, thread = _start_server(path, name=path)
            url = 'http://localhost:%s/' % port
            self['register_teardown'](
                lambda: stop_server(url, thread))
            return url
        os.environ['PATH'] = ":".join(
            [tmp, root, bp, os.environ.get('PATH', '')])
        install_buildout(self.requirements, bp)
        self['index_url'] = index_url = start_index(bp)
        self['index_url2'] = index_url2 = start_index(testd)
        bsettings = {'index': index_url, 'index2': index_url2}
        self['globs'] = globals()
        self['globs'].update(locals())
        self['eggp'] = os.path.join(bp, 'foo')
        self['dl'] = os.path.join(bp, 'dl')
        os.chdir(bp)
        touch('buildout.cfg')
        bootstrap()
        self['opath'] = os.environ['PATH']
        cwd = pkg_resources.resource_filename(
            'minitage.recipe.egg', 'tests')
        root = D(D(D(D(D(cwd)))))
        rbin = os.path.join(root, 'bin')
        if not rbin in self['opath']:
            os.environ['PATH'] = ":".join(
                [rbin, self['opath']])

    def tearDown(self):
        for f in self['__tear_downs']:
            f()
        os.environ['PATH'] = self['opath']

    def testSetUp(self):
        os.chdir(self['bp'])
        for p in (self['eggp'], self['dl']):
            if not os.path.exists(p):
                mkdir(p)

    def testTearDown(self):
        os.chdir(self['bp'])
        cleandist()
        clean()
        for p in (self['eggp'], self['dl']):
            if os.path.exists(p):
                rmdir(p)

MINITAGE_RECIPE_EGG_FIXTURE = Layer()


class IntegrationLayer(Layer):
    """."""
    defaultBases = (MINITAGE_RECIPE_EGG_FIXTURE,)


class FunctionnalLayer(IntegrationLayer):
    """."""
    defaultBases = (MINITAGE_RECIPE_EGG_FIXTURE,)

MINITAGE_RECIPE_EGG_INTEGRATION_TESTING = IntegrationLayer()
MINITAGE_RECIPE_EGG_FUNCTIONAL_TESTING = FunctionnalLayer()
# vim:set et sts=4 ts=4 tw=80:
