#!/bin/bash
cd "$(dirname "$0")"

# Find a Python that has tkinter (the GUI dep). The macOS system python at
# /usr/bin/python3 ships with Tk; some Homebrew pythons don't unless python-tk
# is also installed.
PYTHON=""
for candidate in \
    /usr/bin/python3 \
    python3 \
    python3.12 python3.11 python3.10 python3.13 python3.14; do
    if command -v "$candidate" >/dev/null 2>&1 && \
       "$candidate" -c 'import tkinter' >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Could not find a Python install with tkinter."
    echo "On macOS the bundled /usr/bin/python3 normally has it."
    echo "If you use Homebrew Python, install Tk with:  brew install python-tk"
    read -p "Press Enter to close..."
    exit 1
fi

"$PYTHON" -m dw_compare --gui
status=$?
if [ $status -ne 0 ]; then
    read -p "Press Enter to close..."
fi
exit $status
