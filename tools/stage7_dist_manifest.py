#!/usr/bin/env python3
"""Create or verify a deterministic SHA-256 manifest for a Stage VII production dist tree."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "efl-stage7-dist-manifest-1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(dist: Path) -> dict[str, Any]:
    if not dist.is_dir():
        raise ValueError(f"dist directory does not exist: {dist}")

    entries: list[dict[str, Any]] = []
    for path in sorted(dist.rglob("*"), key=lambda item: item.relative_to(dist).as_posix()):
        if path.is_symlink():
            raise ValueError(f"symlink is forbidden in production artifact: {path.relative_to(dist).as_posix()}")
        if not path.is_file():
            continue
        relative = path.relative_to(dist).as_posix()
        entries.append({"path": relative, "size": path.stat().st_size, "sha256": _sha256(path)})

    if not entries:
        raise ValueError("production dist tree is empty")

    canonical_entries = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {
        "schema_version": SCHEMA,
        "artifact_root": "dist",
        "file_count": len(entries),
        "total_bytes": sum(int(entry["size"]) for entry in entries),
        "tree_sha256": hashlib.sha256(canonical_entries).hexdigest(),
        "files": entries,
    }


def write_manifest(dist: Path, manifest_path: Path) -> None:
    manifest = build_manifest(dist)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"STAGE VII DIST MANIFEST: WRITE PASS ({manifest['file_count']} files, {manifest['tree_sha256']})")


def verify_manifest(dist: Path, manifest_path: Path) -> None:
    if not manifest_path.is_file():
        raise ValueError(f"manifest does not exist: {manifest_path}")
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = build_manifest(dist)
    if expected != actual:
        raise ValueError("production dist tree does not match the recorded Stage VII manifest")
    print(f"STAGE VII DIST MANIFEST: VERIFY PASS ({actual['file_count']} files, {actual['tree_sha256']})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("write", "verify"))
    parser.add_argument("dist", type=Path)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    try:
        if args.mode == "write":
            write_manifest(args.dist, args.manifest)
        else:
            verify_manifest(args.dist, args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"STAGE VII DIST MANIFEST: FAIL - {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
