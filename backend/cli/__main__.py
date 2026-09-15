"""
CLI entry point for backend.cli package.
Allows execution via `python -m backend.cli scaffold_module ...`
"""
import sys
from backend.cli.scaffold import main as scaffold_main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scaffold_module":
        sys.argv.pop(1)
        scaffold_main()
    else:
        scaffold_main()
