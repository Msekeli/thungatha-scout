#!/usr/bin/env python3
"""Enforces repository-wide source-file size limit (<= 100 physical lines)."""

import sys
from pathlib import Path

MAX_LINES = 100

# Explicit, documented exceptions for framework entries and generated vendor files.
DOCUMENTED_EXCEPTIONS = {
    # Python package marker
    "backend/scout/__init__.py",
    # Vite bootstrap entry point
    "frontend/src/main.tsx",
    # Vite ambient type declarations
    "frontend/src/vite-env.d.ts",
    # Generated Radix UI primitives from shadcn/ui (components.json)
    "frontend/src/components/ui/dropdown-menu.tsx",
    "frontend/src/components/ui/select.tsx",
    "frontend/src/components/ui/sheet.tsx",
    "frontend/src/components/ui/dialog.tsx",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "__pycache__",
    ".egg-info",
    "thungatha_scout_backend.egg-info",
}

SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".css"}


def check_file_line_limits(root_dir: Path) -> dict[str, int]:
    violations: dict[str, int] = {}
    scan_roots = [
        root_dir / "backend",
        root_dir / "frontend" / "src",
        root_dir / "scripts",
    ]

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for file_path in scan_root.rglob("*"):
            if not file_path.is_file():
                continue
            if any(ignored in file_path.parts for ignored in IGNORED_DIRECTORIES):
                continue
            if file_path.suffix not in SOURCE_EXTENSIONS:
                continue

            rel_path = file_path.relative_to(root_dir).as_posix()
            if rel_path in DOCUMENTED_EXCEPTIONS:
                continue

            line_count = len(file_path.read_text(encoding="utf-8").splitlines())
            if line_count > MAX_LINES:
                violations[rel_path] = line_count

    return violations


def main() -> int:
    root_dir = Path(__file__).resolve().parents[1]
    violations = check_file_line_limits(root_dir)

    if violations:
        print(f"Error: {len(violations)} source file(s) exceed {MAX_LINES} physical lines:")
        for path, count in sorted(violations.items(), key=lambda x: -x[1]):
            print(f"  {count:>4} lines: {path}")
        print("\nEvery non-exempt handwritten source file must remain <= 100 physical lines.")
        return 1

    print(f"Success: All scanned source files satisfy the <= {MAX_LINES} physical line limit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
