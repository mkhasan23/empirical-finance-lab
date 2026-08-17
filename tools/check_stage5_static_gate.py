#!/usr/bin/env python3
"""Static/pre-browser Stage V gate. Real browser parity is enforced in GitHub Actions."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

# Frozen validation corpus must still pass.
proc = subprocess.run(["python", "tools/check_corpus_integrity.py"], cwd=ROOT, text=True, capture_output=True)
if proc.returncode != 0:
    errors.append("Stage III corpus integrity failed")

# Generated package must correspond to current Python source.
subprocess.run(["python", "tools/build_stage5_browser_assets.py"], cwd=ROOT, check=True)
core = json.loads((ROOT / "web/public/efl-core.json").read_text())
for item in core["files"]:
    source = (ROOT / "src" / item["path"]).read_bytes()
    if hashlib.sha256(source).hexdigest() != item["sha256"]:
        errors.append(f"browser source bundle drift: {item['path']}")

runtime = json.loads((ROOT / "web/public/stage5-runtime-pin.json").read_text())
if runtime["pyodide_version"] != "314.0.4":
    errors.append("Pyodide runtime is not pinned to 314.0.4")
if runtime.get("expected_browser_python") != "3.14.2":
    errors.append("Browser Python runtime is not pinned to 3.14.2")
if runtime.get("expected_browser_numpy") != "2.4.3" or runtime.get("expected_browser_scipy") != "1.18.0":
    errors.append("Browser NumPy/SciPy runtime pins drifted")


package = json.loads((ROOT / "web/package.json").read_text())
expected_dev_dependencies = {
    "@playwright/test": "1.62.0",
    "@types/node": "24.13.3",
    "typescript": "5.9.3",
    "vite": "8.2.1",
    "vitest": "4.1.10",
}
for name, version in expected_dev_dependencies.items():
    if package.get("devDependencies", {}).get(name) != version:
        errors.append(f"frontend dependency pin drift: {name} expected {version}")

browser_tsconfig = json.loads((ROOT / "web/tsconfig.json").read_text())
browser_types = browser_tsconfig.get("compilerOptions", {}).get("types", [])
if "node" in browser_types:
    errors.append("browser tsconfig must not expose Node globals")
if browser_tsconfig.get("include") != ["src/**/*.ts"]:
    errors.append("browser tsconfig include boundary drifted")

node_tsconfig_path = ROOT / "web/tsconfig.node.json"
if not node_tsconfig_path.exists():
    errors.append("Node/tooling tsconfig is missing")
else:
    node_tsconfig = json.loads(node_tsconfig_path.read_text())
    node_types = node_tsconfig.get("compilerOptions", {}).get("types", [])
    if "node" not in node_types:
        errors.append("Node/tooling tsconfig does not explicitly enable Node types")
    node_includes = set(node_tsconfig.get("include", []))
    required_node_includes = {"vite.config.ts", "vitest.config.ts", "playwright.config.ts", "tests/**/*.ts", "src/global.d.ts"}
    if not required_node_includes.issubset(node_includes):
        errors.append("Node/tooling tsconfig does not cover all Node-executed config/test files")

typecheck_script = package.get("scripts", {}).get("typecheck", "")
if "typecheck:browser" not in typecheck_script or "typecheck:node" not in typecheck_script:
    errors.append("typecheck script does not enforce separate browser and Node/tooling configs")

vitest_config_path = ROOT / "web/vitest.config.ts"
if not vitest_config_path.exists():
    errors.append("Vitest config is missing")
else:
    vitest_config = vitest_config_path.read_text()
    if 'include: ["src/**/*.test.ts"]' not in vitest_config:
        errors.append("Vitest unit-test discovery boundary drifted")

unit_test_script = package.get("scripts", {}).get("test:unit", "")
if "--config vitest.config.ts" not in unit_test_script:
    errors.append("unit-test script does not explicitly use the Vitest boundary config")

build_script = package.get("scripts", {}).get("build", "")
if build_script.strip() != "vite build":
    errors.append("browser build must be pure Vite and must not regenerate scientific assets")

worker = (ROOT / "web/src/eflWorker.ts").read_text()
if "efl_raw_csv_text" not in worker or "run_analysis" not in worker:
    errors.append("worker does not invoke authoritative Python run_analysis path")
if "eval(" in worker or "new Function" in worker:
    errors.append("worker contains arbitrary JavaScript evaluation surface")
if "CORE_BUNDLE_ORIGIN_FORBIDDEN" not in worker:
    errors.append("worker does not enforce same-origin authoritative core bundle")

client = (ROOT / "web/src/engineClient.ts").read_text()
if "PUBLIC_PERMUTATION_MIN" not in client:
    errors.append("browser client does not enforce the Stage IV minimum permutation count")


if "progress phase" not in client or "pending.timer = armTimer()" not in client:
    errors.append("browser client does not refresh/report the INIT stall watchdog on valid progress")

required_init_phases = {
    "importing_pyodide_module",
    "initializing_python_runtime",
    "loading_numpy",
    "loading_scipy",
    "scientific_runtime_loaded",
    "fetching_core_bundle",
    "verifying_core_bundle",
    "installing_core_bundle",
    "importing_efl_core",
}
for phase in required_init_phases:
    if phase not in worker:
        errors.append(f"worker initialization progress phase missing: {phase}")


gitignore = (ROOT / ".gitignore").read_text()
for generated in (
    "web/public/efl-core.json",
    "web/public/stage5-parity-cases.json",
    "web/public/stage5-runtime-pin.json",
):
    if generated not in gitignore:
        errors.append(f"generated Stage V browser asset is not ignored: {generated}")

workflow = (ROOT / ".github/workflows/browser-runtime.yml").read_text()
for browser in ("chromium", "firefox", "webkit"):
    if browser not in workflow:
        errors.append(f"Stage V CI browser matrix missing: {browser}")
if "matrix:" not in workflow or "--project=${{ matrix.browser }}" not in workflow:
    errors.append("Stage V CI does not isolate browser parity by matrix project")

if "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7" not in workflow or "name: stage5-browser-assets" not in workflow:
    errors.append("Stage V preflight does not publish the authoritative browser asset artifact with the approved immutable action pin")
if "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8" not in workflow or "path: web/public" not in workflow:
    errors.append("Stage V browser jobs do not consume the authoritative preflight asset artifact with the approved immutable action pin")

browser_section = workflow.split("  browser-runtime:", 1)[1] if "  browser-runtime:" in workflow else ""
if "python tools/build_stage5_browser_assets.py" in browser_section:
    errors.append("Stage V browser jobs must not regenerate scientific parity assets")
if "Set up Python" in browser_section:
    errors.append("Stage V browser jobs should not install a redundant scientific Python environment")

if errors:
    print("STAGE V STATIC GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)
print("STAGE V STATIC GATE: PASS")
