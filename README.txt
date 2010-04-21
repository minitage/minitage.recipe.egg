******************************************************************************
Recipe for compiling and installing software with or without minitage
******************************************************************************

.. contents::

=======================
Introduction
=======================

The egg has those entry point:

    - *egg*: install python eggs / packages 'setuptoolisables'




The reasons why i have rewrite yet another buildout recipes builder are:

    - Support for downloading stuff
    - Do not rely on easy_install dependency system
    - Support on the fly patchs for eggs and other distribution.
    - Support multiple hooks at each stage of the build system.
    - Robust offline mode
    - We like pypi, but offer a mode to scan for eggs without need to check
      the index,
    - Support malformed or not indexed distributions.
      In other terms, we provide an url, and the recipe builds it, that's all.
    - Support automaticly minitage dependencies and rpath linking.



You can browse the code on minitage's following resources:

    - http://git.minitage.org/git/minitage/eggs/minitage.recipe.egg/
    - http://www.minitage.org/trac/browser/minitage/eggs/minitage.recipe.egg



You can migrate your buldouts without any effort with buildout.minitagificator:

    - http://pypi.python.org/pypi/buildout.minitagificator

======================================
Makina Corpus sponsorised software
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

  .. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
  .. _makinacom:  http://www.makina-corpus.com



