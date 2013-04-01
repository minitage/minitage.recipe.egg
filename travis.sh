#!/usr/bin/env bash
git commit -am "before build trigger"
echo >>buildout.cfg
git commit -am "build trigger"
git reset --hard HEAD^
git push --force origin master:travis
