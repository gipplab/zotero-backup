#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_files() {
  cd data
  git add -A
  git commit -am "[skip ci] Update backup data (build $TRAVIS_BUILD_NUMBER)"
  export GIT_SSH_COMMAND="ssh -i $TRAVIS_BUILD_DIR/github_deploy_key"
  git push origin HEAD:master
  cd ..
  git remote add ssh git@github.com:ag-gipp/zotero-backup.git
  git fetch ssh
  git add -A
  git commit -am "[skip ci] Update link to backup data (build $TRAVIS_BUILD_NUMBER)"
  export GIT_SSH_COMMAND="ssh -i $TRAVIS_BUILD_DIR/github_deploy_key_2"
  git push ssh HEAD:master
}


setup_git
commit_files
