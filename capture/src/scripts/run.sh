#!/bin/bash

# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


if [ -z "$DISPLAY" ] || [ "$XDG_SESSION_TYPE" != "x11" ] && [ "$XDG_SESSION_TYPE" != "wayland" ]; then
    echo "Error: The script can only be executed on a graphical interface."
    exit 1
fi

if [ -z "$TERM" ] || [ "$TERM" = "dumb" ]; then
    lxterminal -e "$0"
    exit 0
fi

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
VENV_PATH="$(readlink -f "$SCRIPT_DIR/../../../../.venv")"
APP_PATH="$(readlink -f "$SCRIPT_DIR/../main.py")"

if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Error: Can't find the virtual env '$VENV_PATH'"
    read -p "Enter to finish..."
    exit 1
fi

if [ ! -f "$APP_PATH" ]; then
    echo "Error: Can't find the app env '$APP_PATH'"
    read -p "Enter to finish..."
    exit 1
fi

echo "Activating virtual env..."
source "$VENV_PATH/bin/activate"

if [ $? -eq 0 ]; then
    echo "Running app..."
    python "$APP_PATH"
    EXIT_CODE=$?
    deactivate
    echo "App finish with exit code: $EXIT_CODE"
else
    echo "Error: Can't activate virtual env."
    read -p "Enter to finish..."
    exit 1
fi

read -p "Enter to finish..."
