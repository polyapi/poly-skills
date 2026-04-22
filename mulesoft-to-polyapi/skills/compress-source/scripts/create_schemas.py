#!/usr/bin/env python3
"""Run the shared generate-schemas script from the compress-source skill."""

from pathlib import Path
import runpy


def main() -> None:
    target = (
        Path(__file__).resolve().parents[2]
        / "generate-schemas"
        / "scripts"
        / "create_schemas.py"
    )
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
