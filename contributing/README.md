# Contribution Guide

## Development Environment:

#### You'll need to install the following dependencies:

1) shellcheck  
2) python 3.6
3) pipenv


#### On OSX This looks like:
```bash
$ brew install shellcheck pipenv
```

## Recommend Installing ASDF to manage Python Versions

```bash
$ git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.7.5
```

## Use ASDF To Install Python 3.6.0

```bash
$ git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.7.5
$ source contributing/scripts/dev
$ asdf install python 3.6.0
```

## Use the dev scripts to help you work with the code base

```bash
$ source contributing/scripts/dev
$ dev
Valid Commands:
 - lint [time] [v]
 - pipeline
 - setup
 - shell
 - test
```

## Setup a dev environment

```bash
$ source contributing/scripts/dev
$ dev setup
```
