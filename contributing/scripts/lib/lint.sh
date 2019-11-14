#!/bin/bash

set -e

background_pylint() {
  bash ./scripts/lib/pylint.sh "${1}"
}

lint() {

  if [[ "$1" == 'time' ]]; then
    shift
    TIMINGS="TIMINGS"
  fi

  if [[ "$1" == 'v' ]]; then
    VERBOSE_ISORT=()
    VERBOSE_BLACK=("-v")
  else
    VERBOSE_ISORT=("-q")
    VERBOSE_BLACK=()
  fi

  MYPYPATH="${PROJECTNAME}/stubs/"
  export MYPYPATH

  source_enviroment

  set -e

  shellcheck -x contributing/scripts/*.sh
  shellcheck -x contributing/scripts/lib/*.sh
  shellcheck -x contributing/scripts/hooks/*

  # Code Cleaners
  echo '- black ...'
  black "${VERBOSE_BLACK[@]}" -q -l 80 examples flask_restful_swagger tests setup.py

  echo '- isort ...'
  isort "${VERBOSE_ISORT[@]}" -y

  echo '- flake8 ...'
  if [[ -z "${TIMINGS}" ]]; then
    flake8
  else
    time flake8
  fi

  set +e

}
