#!/bin/bash

set -e

build_documentation() {

  echo "Generating Documentation ..."

  source_enviroment

  set -e

  pushd "${PROJECTHOME}/${PROJECTNAME}" > /dev/null
    rm -rf documentation-build
    make html
  popd > /dev/null

}

deploy_documentation() {

  echo "Deploying Documentation ..."

  source_enviroment

  set -e

  pushd "${PROJECTHOME}/${PROJECTNAME}" > /dev/null
    current_branch="$(git rev-parse --abbrev-ref HEAD)"
    git checkout --orphan gh-pages
    touch documentation-build/html/.nojekyll
    git add -f "documentation-build"
    git commit -n -m 'Documentation'
    git push -fu origin gh-pages
    git checkout "${current_branch}"
    git branch -D gh-pages
  popd > /dev/null

}