#!/usr/bin/env bash

# shellcheck disable=SC1117
build_wheel() {

  set -e

  BRed='\033[31m'         # Red
  BGreen='\033[32m'       # Green
  NC="\033[0m"            # Color Reset

  OWNER="${OWNER}"
  REPO="${REPO}"
  TAG="${TAG}"

  source_enviroment
  pushd "${PROJECT_HOME}"  > /dev/null

    if [[ -f .gittoken ]]; then
      GITHUB_TOKEN=$(cat .gittoken)
      export GITHUB_TOKEN
    fi

    rm -rf dist ./*.egg-info build
    python setup.py bdist_wheel
    mv dist/*.whl .
    rm -rf dist ./*.egg-info build
    echo -e "\\n${BGreen}Built:${NC} ${BRed}$(ls ./*.whl)${NC}"

    if [[ -n ${GITHUB_TOKEN} ]]; then
      ./scripts/common/upload.sh _GITHUB_API_TOKEN="${GITHUB_TOKEN}" _OWNER="${OWNER}" _REPO="${REPO}" _TAG="${TAG}" _FILENAME="$(ls ./*.whl)"
      rm ./*.whl
    else
      echo -e "Set the environment variable ${BRed}GITHUB_TOKEN${NC} to automate the upload to github.\\n"
    fi

  popd  > /dev/null

}