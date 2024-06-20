#!/bin/bash

CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/halfass-it/bot"
VENV="$CACHE/.venv"
POETRY="$VENV/bin/poetry"

mkdir -p "$CACHE"
if [ ! -d "$VENV" ]; then
    $POETRY env use "$VENV"
    $POETRY install
fi

$POETRY run main $DISCORD_BOT_TOKEN $CACHE run
