#!/bin/sh

CACHE="$XDG_CACHE_HOME/halfass-it/bot"
VENV="$CACHE/.venv"
PYTHON="/usr/bin/python3.12"
PIP="$VENV/bin/pip"
POETRY="$VENV/bin/poetry"
mkdir -p $CACHE
if [ -d $VENV ]; then
    rm -rf $VENV
fi
$PYTHON -m venv $VENV
if [ ! -d "$VENV" ]; then
    $POETRY env use "$VENV"
    $POETRY install
fi
$PIP install --upgrade pip
$PIP install wheel setuptools poetry python-dotenv ruff
$POETRY install
