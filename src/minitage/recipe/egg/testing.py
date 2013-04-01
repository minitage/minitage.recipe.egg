#!/usr/bin/env python
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from plone.testing.layer import Layer as Base

import copy

import pkg_resources
import os

from minitage.core import testing

J = testing.J
B = testing.B
D = testing.D

from minitage.core import testing


class Layer(Base):

    defaultBases = (testing.LAYER,)
    requirements = ('minitage.recipe.egg[test]',)

    def setUp(self):
        tmp = self['p']
        bp = self["bp"] = J(
            tmp, 'root', 'categ', 'test')
        testd = J(bp, 'test')
        if not os.path.exists(testd):
            os.makedirs(testd)
        self['index_url'] = self['start_index'](bp)
        self['index_url2'] = self['start_index'](testd)
        bsettings = self['bsettings'] = {
            'index': self['index_url'],
            'index2': self['index_url2']}
        self['eggp'] = J(bp, 'foo')
        self['dl'] = J(bp, 'dl')
        self['opath'] = os.environ['PATH']
        cwd = pkg_resources.resource_filename(
            'minitage.recipe.egg', 'tests')
        testing.LAYER.add_path(self.requirements)
        testing.install_buildout(bp, self.requirements)
        self['globs'] = copy.copy(self['globs'])
        self['globs'].update(globals())
        self['globs'].update(locals())

    def tearDown(self):
        if os.path.exists(self['bp']):
            testing.rmdir(self['bp'])

    def testSetUp(self):
        os.chdir(self['bp'])
        for ep in (self['eggp'], self['dl']):
            if not os.path.exists(ep):
                testing.mkdir(ep)

    def testTearDown(self):
        os.chdir(self['bp'])
        testing.cleandist()
        testing.clean()
        for ep in (self['eggp'], self['dl']):
            if os.path.exists(ep):
                testing.rmdir(ep)


LAYER = Layer()
# vim:set et sts=4 ts=4 tw=80:
