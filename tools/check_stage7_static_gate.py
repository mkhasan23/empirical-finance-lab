#!/usr/bin/env python3
"""Static/pre-deployment Stage VII gate for reproducible GitHub Pages candidates."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

# Stage VII may harden release/deployment plumbing, but the accepted Stage VI scientific/application foundation must remain green.
proc = subprocess.run(
    ["python", "tools/check_stage6_static_gate.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
if proc.returncode != 0:
    errors.append("Stage VI static gate failed")

supply_chain_proc = subprocess.run(
    ["python", "tools/check_stage7_c2_supply_chain_gate.py"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
if supply_chain_proc.returncode != 0:
    errors.append("Stage VII-C2 supply-chain gate failed")

package_path = ROOT / "web/package.json"
lock_path = ROOT / "web/package-lock.json"
if not package_path.is_file():
    errors.append("web/package.json is missing")
else:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    if scripts.get("build") != "vite build":
        errors.append("Stage V/VI build authority drifted; web build must remain exactly 'vite build'")
    if scripts.get("build:pages") != "vite build --mode github-pages":
        errors.append("GitHub Pages production build script is missing or drifted")
    if scripts.get("preview:pages") != "vite preview --mode github-pages --host 127.0.0.1 --port 4173":
        errors.append("GitHub Pages production preview script is missing or drifted")
    if scripts.get("test:e2e:stage7") != "playwright test --config=playwright.stage7.config.ts":
        errors.append("Stage VII production-like Playwright script is missing or drifted")
    if scripts.get("test:e2e:stage7:live") != "playwright test --config=playwright.stage7.live.config.ts":
        errors.append("Stage VII live deployed-site Playwright script is missing or drifted")
    if package.get("dependencies"):
        errors.append("Stage VII must not introduce frontend runtime npm dependencies")

if not lock_path.is_file():
    errors.append("web/package-lock.json is required for deterministic CI installs")
else:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    if lock.get("lockfileVersion") != 3:
        errors.append("frontend package-lock must use lockfileVersion 3")
    root_lock = lock.get("packages", {}).get("", {})
    if package_path.is_file():
        package = json.loads(package_path.read_text(encoding="utf-8"))
        if root_lock.get("devDependencies") != package.get("devDependencies"):
            errors.append("package-lock root devDependencies do not match package.json exactly")

vite = (ROOT / "web/vite.config.ts").read_text(encoding="utf-8")
if 'mode === "github-pages"' not in vite or '"/empirical-finance-lab/"' not in vite:
    errors.append("Vite does not preserve the required /empirical-finance-lab/ production base path")

node_config_path = ROOT / "web/tsconfig.node.json"
if not node_config_path.is_file():
    errors.append("Node/tooling TypeScript config is missing")
else:
    node_config = json.loads(node_config_path.read_text(encoding="utf-8"))
    includes = node_config.get("include", [])
    if "playwright.stage7.config.ts" not in includes:
        errors.append("Stage VII Playwright config is outside the Node/tooling typecheck boundary")
    if "playwright.stage7.live.config.ts" not in includes:
        errors.append("Stage VII live Playwright config is outside the Node/tooling typecheck boundary")
    if "tests-live/**/*.ts" not in includes:
        errors.append("Stage VII live tests are outside the Node/tooling typecheck boundary")

stage7_playwright = ROOT / "web/playwright.stage7.config.ts"
if not stage7_playwright.is_file():
    errors.append("Stage VII Playwright config is missing")
else:
    config = stage7_playwright.read_text(encoding="utf-8")
    for required in (
        "http://127.0.0.1:4173/empirical-finance-lab/",
        'testMatch: "stage7.spec.ts"',
        'name: "chromium"',
        'command: "npm run preview:pages"',
    ):
        if required not in config:
            errors.append(f"Stage VII production-like Playwright config drifted: {required}")

stage7_test = ROOT / "web/tests/stage7.spec.ts"
if not stage7_test.is_file():
    errors.append("Stage VII production-like browser smoke test is missing")
else:
    test_text = stage7_test.read_text(encoding="utf-8")
    for required in (
        'const BASE_PATH = "/empirical-finance-lab/"',
        'window.__EFL_STAGE5__.initialize()',
        'window.__EFL_STAGE5__.runFixture("KA-003")',
        'pathname === `${BASE_PATH}efl-core.json`',
        'expect(analysisRequests, "production-like scientific analysis emitted a network request").toEqual([])',
        'expect(runtime.efl_version).toBe("0.1.1")',
    ):
        if required not in test_text:
            errors.append(f"Stage VII production browser invariant missing: {required}")

stage7_live_playwright = ROOT / "web/playwright.stage7.live.config.ts"
if not stage7_live_playwright.is_file():
    errors.append("Stage VII live deployed-site Playwright config is missing")
else:
    live_config = stage7_live_playwright.read_text(encoding="utf-8")
    for required in (
        "process.env.EFL_STAGE7_LIVE_URL",
        'liveUrl.protocol !== "https:"',
        'liveUrl.hostname !== "mkhasan23.github.io"',
        'liveUrl.pathname !== "/empirical-finance-lab/"',
        'testDir: "./tests-live"',
        'testMatch: "stage7.live.spec.ts"',
        'name: "chromium"',
    ):
        if required not in live_config:
            errors.append(f"Stage VII live Playwright config drifted: {required}")
    if "webServer:" in live_config:
        errors.append("Stage VII live Playwright config must target the deployed HTTPS site and must not start a local web server")

stage7_live_test = ROOT / "web/tests-live/stage7.live.spec.ts"
if not stage7_live_test.is_file():
    errors.append("Stage VII live deployed-site browser test is missing")
else:
    live_test_text = stage7_live_test.read_text(encoding="utf-8")
    for required in (
        'const BASE_PATH = "/empirical-finance-lab/"',
        'const EXPECTED_ORIGIN = "https://mkhasan23.github.io"',
        'const MANIFEST_SCHEMA = "efl-stage7-dist-manifest-1"',
        'process.env.EFL_STAGE7_MANIFEST',
        'createHash("sha256")',
        'window.__EFL_STAGE5__.initialize()',
        'window.__EFL_STAGE5__.runFixture("KA-003")',
        'pathname === `${BASE_PATH}efl-core.json`',
        'expect(analysisRequests, "live production scientific analysis emitted a network request").toEqual([])',
        'toBe("cdn.jsdelivr.net")',
        'expect(runtime.efl_version).toBe("0.1.1")',
    ):
        if required not in live_test_text:
            errors.append(f"Stage VII live deployed-site invariant missing: {required}")

manifest_tool = ROOT / "tools/stage7_dist_manifest.py"
if not manifest_tool.is_file():
    errors.append("Stage VII deterministic dist manifest tool is missing")
else:
    manifest_text = manifest_tool.read_text(encoding="utf-8")
    for required in ("efl-stage7-dist-manifest-1", "tree_sha256", "symlink is forbidden"):
        if required not in manifest_text:
            errors.append(f"Stage VII dist-manifest invariant missing: {required}")

workflow_path = ROOT / ".github/workflows/release-hardening.yml"
if not workflow_path.is_file():
    errors.append("Stage VII release-hardening workflow is missing")
else:
    workflow = workflow_path.read_text(encoding="utf-8")
    for required in (
        "push:",
        "pull_request:",
        "workflow_dispatch:",
        "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6",
        "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6",
        "actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38 # v6",
        "node-version: '24'",
        "npm ci --no-audit --no-fund",
        "npm run build:pages",
        "npm run test:e2e:stage7",
        "npm run test:e2e:stage7:live",
        "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7",
        "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8",
        "actions/configure-pages@45bfe0192ca1faeb007ade9deae92b16b8254a0d # v6",
        "actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9 # v5",
        "actions/deploy-pages@cd2ce8fcbc39b97be8ca5fce6e763baed58fa128 # v5",
        "pages: write",
        "id-token: write",
        "name: github-pages",
        "github.ref == 'refs/heads/main'",
        "inputs.deploy == true",
        "[deploy-candidate]",
        "python tools/stage7_dist_manifest.py write",
        "python tools/stage7_dist_manifest.py verify",
        "page_url: ${{ steps.deployment.outputs.page_url }}",
        "verify-live:",
        "needs: deploy",
        "EFL_STAGE7_LIVE_URL: ${{ needs.deploy.outputs.page_url }}",
        "EFL_STAGE7_MANIFEST: ${{ github.workspace }}/stage7-evidence/stage7-dist-manifest.json",
    ):
        if required not in workflow:
            errors.append(f"Stage VII release workflow invariant missing: {required}")
    if "npm install " in workflow:
        errors.append("Stage VII release workflow must use npm ci, not npm install")

    deploy_marker = "\n  deploy:\n"
    live_marker = "\n  verify-live:\n"
    deploy_section = ""
    if deploy_marker in workflow:
        deploy_section = workflow.split(deploy_marker, 1)[1]
        if live_marker in deploy_section:
            deploy_section = deploy_section.split(live_marker, 1)[0]
    if "npm run build" in deploy_section:
        errors.append("Stage VII deploy job must reuse the tested artifact and must not rebuild")
    if deploy_section:
        verify_pos = deploy_section.find("Verify downloaded production artifact")
        pages_upload_pos = deploy_section.find("Upload GitHub Pages artifact")
        if verify_pos < 0 or pages_upload_pos < 0 or verify_pos > pages_upload_pos:
            errors.append("Stage VII deploy job must verify the downloaded artifact before Pages packaging")

    live_section = workflow.split(live_marker, 1)[1] if live_marker in workflow else ""
    if live_section:
        if "npm run build" in live_section:
            errors.append("Stage VII live deployed-site job must verify the published artifact and must not rebuild")
        evidence_pos = live_section.find("Download production artifact evidence")
        live_test_pos = live_section.find("Verify exact live artifact, runtime parity, and analysis privacy")
        if evidence_pos < 0 or live_test_pos < 0 or evidence_pos > live_test_pos:
            errors.append("Stage VII live deployed-site job must download the build manifest before live verification")

index = (ROOT / "web/index.html").read_text(encoding="utf-8")
if 'content="noindex,nofollow"' in index:
    errors.append("current validated v0.1.1 patch release must be indexable; stale noindex boundary remains")
if "v0.1.1 · validated patch release" not in index:
    errors.append("current v0.1.1 patch-release badge is missing")
if 'id="citation-version">0.1.1' not in index:
    errors.append("current v0.1.1 citation version is missing")

if errors:
    print("STAGE VII STATIC GATE: FAIL")
    for error in errors:
        print(f" - {error}")
    if proc.returncode != 0 and proc.stdout:
        print(proc.stdout.rstrip())
    if proc.returncode != 0 and proc.stderr:
        print(proc.stderr.rstrip())
    if supply_chain_proc.returncode != 0 and supply_chain_proc.stdout:
        print(supply_chain_proc.stdout.rstrip())
    if supply_chain_proc.returncode != 0 and supply_chain_proc.stderr:
        print(supply_chain_proc.stderr.rstrip())
    raise SystemExit(1)

print("STAGE VII STATIC GATE: PASS")
