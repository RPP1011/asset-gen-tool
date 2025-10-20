#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.index import app  # noqa: E402


def main() -> None:
    schema = app.openapi()

    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    output_path = build_dir / "openapi.json"
    output_path.write_text(json.dumps(schema, indent=2))

    types_dir = Path("types/generated")
    types_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
