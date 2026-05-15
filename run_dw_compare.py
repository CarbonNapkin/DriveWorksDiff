"""PyInstaller entry point.

PyInstaller drives a top-level script, not a package's __main__. Pointing
it at this file lets it discover the dw_compare package and bundle every
module that ends up imported from main().

A bare double-click of the packaged executable arrives here with no
command-line arguments, which would otherwise fall into the CLI auto-
detect path and fail because the executable's working directory does not
contain two project files. Promote that case to --gui so the typical end
user gets the graphical UI on launch. Anyone passing real arguments
(running the .exe from a terminal) keeps the CLI behavior.
"""

import sys

from dw_compare.__main__ import main

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('--gui')
    main()
