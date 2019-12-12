#!/bin/bash

set -e


coverage_report() {
  coverage html --fail-under=100
}

sectests() {

  source_enviroment

  set -e

  bandit -r "${PROJECTNAME}" -c .bandit.rc
  pushd "${PROJECTNAME}"  > /dev/null
    safety check
  popd  > /dev/null

  set +e

}

unittests() {

  source_enviroment

  pushd "${PROJECTHOME}" > /dev/null
    pytest --cov=. . "$@"
    coverage_report
  popd > /dev/null

}