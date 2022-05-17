#!/usr/bin/env bash
# This file is part of ddnsp, see <https://github.com/MestreLion/ddnsp>
# Copyright (C) 2022 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>
#
# Convenience wrapper to launch server in development mode
# https://flask.palletsprojects.com/en/2.1.x/cli/
# -----------------------------------------------------------------------------

here=$(dirname "$(readlink -f "$0")")
cd -- "$here" || exit 1

# Any env var can also be set in .env and .flaskenv if python-dotenv is installed
# .env takes precedence, might contain secrets and should not be committed to repo
# .flaskenv can be committed, for settings shared by all deploys

# Any command-line options can also be set with env vars, using the pattern
# "FLASK_COMMAND_OPTION=value", such as FLASK_RUN_PORT=5000
opts=(
)

# Python 3.7 is the current minimum as of v2.1.0 (2022-03-28)
python3.7 -m flask run "${opts[@]}" "$@"
