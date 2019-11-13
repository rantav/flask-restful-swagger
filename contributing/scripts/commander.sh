#!/bin/bash

set -e

PROJECTHOME="$(git rev-parse --show-toplevel)"
PROJECTNAME="flask_restful_swagger"

export PROJECTHOME
export PROJECTNAME

cd "${PROJECTHOME}"

# shellcheck source=contributing/scripts/lib/common.sh
source "$( dirname "${BASH_SOURCE[0]}" )/lib/common.sh"

# shellcheck source=contributing/scripts/lib/documentation.sh
source "$( dirname "${BASH_SOURCE[0]}" )/lib/documentation.sh"

# shellcheck source=contributing/scripts/lib/lint.sh
source "$( dirname "${BASH_SOURCE[0]}" )/lib/lint.sh"

# shellcheck source=contributing/scripts/lib/tests.sh
source "$( dirname "${BASH_SOURCE[0]}" )/lib/tests.sh"


help() {
  echo "${PROJECTNAME}"
}


case $1 in
  'lint')
    shift
    lint "$@"
    ;;
  'pipeline')
    shift
    pipline "$@"
    ;;
  'setup')
    shift
    setup_python "$@"
    ;;
  'shell')
    shift
    source_enviroment
    pipenv shell
    ;;
  'test')
    shift
    unittests "$@"
    ;;
  'shortlist')
    echo "lint pipeline setup shell test"
    ;;
  *)
    echo "Valid Commands:"
    echo ' - lint [time] [v]'
    echo ' - pipeline'
    echo ' - setup'
    echo ' - shell'
    echo ' - test'
    ;;

esac
