"""Make the repo root importable so `import dw_compare` works under pytest
regardless of how/where pytest is invoked."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
