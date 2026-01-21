#!/bin/bash
cd "$(dirname "$0")"
python3 -m dw_compare
read -p "Press Enter to close..."
