"""Punkt wejscia dla PyInstallera. Uruchamia pakiet jolaos jak `python -m jolaos`."""

import sys

from jolaos.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
