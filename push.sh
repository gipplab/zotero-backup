#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_files() {
  cd data
  git add -A
  git commit -am "Update backup data (build $TRAVIS_BUILD_NUMBER)"
  git checkout -b updater origin/master
  cd ..
  git add -A
  git commit -am "Update link to backup data (build $TRAVIS_BUILD_NUMBER)"
  git checkout -b updater origin/master
  git push --recurse-submodules=on-demand
}


setup_git
commit_files
