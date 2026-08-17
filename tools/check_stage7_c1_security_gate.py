#!/usr/bin/env python3
"""Static Stage VII-C1 browser-security gate.

This gate is intentionally additive. It does not replace the accepted Stage VII
release/deployment gate; it protects the document CSP/referrer-policy contract
before a Pages production build is emitted.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

EXPECTED_CSP = (
    "default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; "
    "style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
    "worker-src 'self'; frame-src 'none'; media-src 'none'; manifest-src 'self'; "
    "form-action 'self'"
)

package_path = ROOT / "web/package.json"
if not package_path.is_file():
    errors.append("web/package.json is missing")
else:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    expected_prebuild = "python ../tools/check_stage7_c1_security_gate.py && python ../tools/check_stage7_d2_repro_gate.py"
    if package.get("scripts", {}).get("prebuild:pages") != expected_prebuild:
        errors.append("Pages build does not automatically invoke the Stage VII-C1 security gate before the D2 reproducibility gate")
    if package.get("dependencies"):
        errors.append("Stage VII-C1 must not introduce frontend runtime npm dependencies")

vite_path = ROOT / "web/vite.config.ts"
if not vite_path.is_file():
    errors.append("Vite config is missing")
else:
    vite = vite_path.read_text(encoding="utf-8")
    for required in (
        'export const DOCUMENT_CSP = [',
        'name: "efl-document-security-policy"',
        '"http-equiv": "Content-Security-Policy"',
        'name: "referrer"',
        'content: "no-referrer"',
        'injectTo: "head-prepend"',
    ):
        if required not in vite:
            errors.append(f"document-security Vite contract missing: {required}")
    for directive in EXPECTED_CSP.split("; "):
        if f'"{directive}"' not in vite:
            errors.append(f"document CSP directive missing: {directive}")
    if "cdn.jsdelivr.net" in vite:
        errors.append("document CSP must not grant jsDelivr access to the page context")
    if "'unsafe-inline'" in vite or "'unsafe-eval'" in vite:
        errors.append("document CSP must not permit unsafe-inline or unsafe-eval")

for rel, label in (
    ("web/tests/stage7.spec.ts", "production-like"),
    ("web/tests-live/stage7.live.spec.ts", "live production"),
):
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"Stage VII-C1 {label} security test is missing: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    for required in (
        "EXPECTED_DOCUMENT_CSP",
        'meta[http-equiv="Content-Security-Policy"]',
        'meta[name="referrer"]',
        'toBe("no-referrer")',
        "securitypolicyviolation",
        "__EFL_STAGE7_CSP_VIOLATIONS__",
        "emitted a CSP violation",
    ):
        if required not in text:
            errors.append(f"Stage VII-C1 {label} browser assertion missing: {required}")
    if EXPECTED_CSP not in text:
        errors.append(f"Stage VII-C1 {label} browser test does not pin the exact document CSP")

security_path = ROOT / "SECURITY.md"
if not security_path.is_file():
    errors.append("SECURITY.md is missing")
else:
    security = security_path.read_text(encoding="utf-8")
    for required in (
        "Content Security Policy",
        "Referrer Policy",
        "cdn.jsdelivr.net",
        "same-origin",
        "zero network requests during scientific analysis",
        "does not claim that the document CSP governs the worker's internal fetches",
    ):
        if required not in security:
            errors.append(f"SECURITY.md Stage VII-C1 boundary missing: {required}")

spec_path = ROOT / "docs/specifications/STAGE_VII_RELEASE_HARDENING.md"
if not spec_path.is_file():
    errors.append("Stage VII specification is missing")
else:
    spec = spec_path.read_text(encoding="utf-8")
    for required in (
        "## Browser security boundary contract",
        "Content Security Policy",
        "Referrer Policy",
        "worker-src 'self'",
        "cdn.jsdelivr.net",
        "worker's internal network policy",
        "securitypolicyviolation",
    ):
        if required not in spec:
            errors.append(f"Stage VII-C1 specification invariant missing: {required}")

if errors:
    print("STAGE VII-C1 SECURITY GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print("STAGE VII-C1 SECURITY GATE: PASS")
