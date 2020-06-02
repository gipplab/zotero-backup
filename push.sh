#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_files() {
  cd data
  git add -A
  git commit -am "[skip ci] Update backup data (build $TRAVIS_BUILD_NUMBER)"
  git checkout -b updater
  git branch -u origin/master
  git rebase
  git push
  cd ..
  git add -A
  git commit -am "[skip ci] Update link to backup data (build $TRAVIS_BUILD_NUMBER)"
  git checkout -b updater
  git remote add ssh git@github.com:ag-gipp/zotero-backup.git
  git fetch ssh
  git branch -u ssh/master
  git rebase
  export GIT_SSH_COMMAND="ssh -i github_deploy_key_2"
  git push ssh updater:master
}


setup_git
commit_files
