#!/bin/bash

setup_python() {

  unvirtualize

  pushd "${PROJECTHOME}"  > /dev/null
    set +e
    pipenv --rm
    set -e
    pipenv --python 3.6
    source_enviroment
    pip install -r docker/requirements-testing.txt
    unvirtualize
  popd  > /dev/null

}

source_enviroment() {

  set -e

  [[ "$1" == "build" ]] && return

  unvirtualize

  # shellcheck disable=SC1090
  source "$(pipenv --venv)/bin/activate"

  pushd "${PROJECTHOME}"  > /dev/null
    cd .git/hooks
    ln -sf ../../scripts/hooks/pre-commit pre-commit
    ln -sf ../../scripts/hooks/post-merge post-merge
  popd  > /dev/null

  set +e

}

unvirtualize() {

  toggle=1

  if [[ -n "${-//[^e]/}" ]]; then set +e; else toggle=0; fi
  if python -c 'import sys; sys.exit(0 if hasattr(sys, "real_prefix") else 1)'; then
    deactivate_present=$(LC_ALL=C type deactivate 2>/dev/null)
    if [[ -n ${deactivate_present} ]]; then
      deactivate
    else
      echo "Exit your shell before you attempt this action."
      exit 127
    fi
  fi
  if [[ "${toggle}" == "1" ]]; then set -e; fi

}
