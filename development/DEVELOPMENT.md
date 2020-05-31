# flask-restful-swagger

A Swagger Spec Extractor for Flask-Restful

## Please Do's!
 - Please use commitizen to normalize your commit messages
 - Please lint your code before sending pull requests

## Development Dependencies

You'll need to install:
 - [Docker](https://www.docker.com/) 
 - [Docker Compose](https://docs.docker.com/compose/install/)

## Setup the Development Environment

Build the development environment container (this takes a few minutes):
- `docker-compose build`

Start the environment container:
- `docker-compose up -d`

Spawn a shell inside the container:
- `./container`

## But I Want to Develop in Python2

Although Python2 is EOL, we still want to support the existing users out there for as long as we can:

Modify the first line of `development/Dockerfile` to:
- `FROM python:2.7-slim`

You should now be able to rebuild your container, and restart your development environment.


If you're switching back and forth between Python2 and 3, you'll need to wipe the compiled bytecode.<br> Run this command inside the container:
- `find . -name *.pyc -delete`

## Install the Project Packages on your Host Machine:
This is useful for making your IDE aware of what's installed in a venv.

- `pip install pipenv`
- `source scripts/dev`
- `dev setup` (Installs the requirements.txt in the `assets` folder.)
- `pipenv --venv` (To get the path of the virtual environment for your IDE.)

## Environment
The [development.env](./development.env) file can be modified to inject environment variable content into the container.

You can override the values set in this file by setting shell ENV variables prior to starting the container:
- `export GIT_HOOKS_PROTECTED_BRANCHES='.*'`
- `docker-compose kill` (Kill the current running container.)
- `docker-compose rm` (Remove the stopped container.)
- `docker-compose up -d` (Restart the dev environment, with a new container, containing the override.)
- `./container`

## Git Hooks
Git hooks are installed that will enforce linting and unit-testing on the specified branches.
The following environment variables can be used to customize this behavior:

- `GIT_HOOKS` (Set this value to 1 to enable the pre-commit hook)
- `GIT_HOOKS_PROTECTED_BRANCHES` (Customize this regex to specify the branches that should enforce the Git Hook on commit.)

## CLI Reference
The CLI is enabled by default inside the container, and is also available on the host machine.<br>
Run the CLI without arguments to see the complete list of available commands: `$ dev`
