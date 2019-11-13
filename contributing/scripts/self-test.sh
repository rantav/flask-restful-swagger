#!/bin/bash

set -exa

echo '- black ...'
black --check -l 80 examples
black --check -l 80 flask_restful_swagger
black --check -l 80 setup.py

echo '- isort ...'
isort -c "${VERBOSE_ISORT[@]}" -y

echo '- flake8 ...'
flake8 flask_restful_swagger
flake8 examples
