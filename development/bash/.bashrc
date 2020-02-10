#!/bin/bash

# Do Not Modify This File, It's Intended To Be Updated From Time to TIme
# INSTEAD: add additional functionality though the .bash_customize file.

PS1='${git_branch}\n${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# Terminal Colors
if [[ -x /usr/bin/dircolors ]]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

set -e
  source /app/scripts/dev
  source /home/user/.bash_git
  source /home/user/.bash_customize
set +e
