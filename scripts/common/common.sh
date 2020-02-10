#!/bin/bash

# Do Not Modify This File, It's Intended To Be Updated From Time to TIme
# INSTEAD: add additional functionality by adding separate library files
# Import your new libraries into the commander.sh script and add them to the CLI.

lint() {

  set -e

  pushd "${PROJECT_HOME}"  > /dev/null
    yapf -i --recursive --style=pep8 "${PROJECT_NAME}/"
    isort -y
  popd  > /dev/null

  lint_check

}

lint_check() {

  set -e

  pushd "${PROJECT_HOME}"  > /dev/null
    isort -c
    flake8
    shellcheck -x scripts/*.sh
    shellcheck -x scripts/common/*.sh
  popd  > /dev/null

}

reinstall_requirements() {

  set -e

  pushd "${PROJECT_HOME}"  > /dev/null
    pip install -r assets/requirements.txt --no-warn-script-location
    pip install -r assets/requirements-dev.txt --no-warn-script-location
  popd  > /dev/null

}


security() {

  set -e

  pushd "${PROJECT_HOME}"  > /dev/null
    bandit -r "${PROJECT_NAME}" -c .bandit.rc
    safety check
  popd  > /dev/null

}

setup_bash() {

  [[ ! -f /etc/container_release ]] && return

  for filename in /app/development/bash/.bash*; do
    echo "Symlinking ${filename} ..."
    ln -sf "${filename}" "/home/user/$(basename "${filename}")"
  done

}

setup_python() {

  unvirtualize

  pushd "${PROJECT_HOME}"  > /dev/null
    if [[ ! -f /etc/container_release ]]; then
      set +e
        pipenv --rm
      set -e
      pipenv --python 3.7
    fi
    source_enviroment
    reinstall_requirements
    unvirtualize
  popd  > /dev/null

}

source_enviroment() {

  if [[ ! -f /etc/container_release ]]; then

    unvirtualize

    # shellcheck disable=SC1090
    source "$(pipenv --venv)/bin/activate"

  fi

  pushd "${PROJECT_HOME}"  > /dev/null
    set +e
      cd .git/hooks
      ln -sf ../../scripts/hooks/pre-commit pre-commit
    set -e
  popd  > /dev/null

}

unittests() {

  set -e

  pushd "${PROJECT_HOME}"  > /dev/null
    if [[ $1 == "coverage" ]]; then
      shift
      set +e
        pytest --cov=. --cov-fail-under=100 "$@"
        exit_code="$?"
        coverage html
      set -e
      exit "${exit_code}"
    else
      pytest "$@"
    fi
  popd  > /dev/null

}

unvirtualize() {

  if [[ ! -f /etc/container_release ]]; then

    toggle=1

    if [[ -n "${-//[^e]/}" ]]; then set +e; else toggle=0; fi
    if python -c 'import sys; sys.exit(0 if hasattr(sys, "real_prefix") else 1)'; then
    deactivate_present=$(LC_ALL=C type deactivate 2>/dev/null)
    if [[ -n ${deactivate_present} ]]; then
      deactivate
    else
      exit
    fi
    fi
    if [[ "${toggle}" == "1" ]]; then set -e; fi

  fi

}
