#!/usr/bin/env python3
"""Stage VII-E2 gate: semantic accessibility, keyboard behavior, and responsive proof contract."""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "web" / "index.html"
STYLES = ROOT / "web" / "src" / "styles.css"
APPLICATION = ROOT / "web" / "src" / "application.ts"
RESULTS = ROOT / "web" / "src" / "resultsView.ts"
STAGE7_TEST = ROOT / "web" / "tests" / "stage7.spec.ts"
SPEC = ROOT / "docs" / "specifications" / "STAGE_VII_E2_ACCESSIBILITY_RESPONSIVE.md"

errors: list[str] = []
for path in (INDEX, STYLES, APPLICATION, RESULTS, STAGE7_TEST, SPEC):
    if not path.is_file():
        errors.append(f"required Stage VII-E2 file is missing: {path.relative_to(ROOT)}")

class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.tabs: list[dict[str, str]] = []
        self.panels: dict[str, dict[str, str]] = {}
        self.main: dict[str, str] | None = None
        self.progress: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "main" and data.get("id") == "workspace":
            self.main = data
        if tag == "progress" and data.get("id") == "analysis-progress":
            self.progress = data
        if data.get("role") == "tab":
            self.tabs.append(data)
        if data.get("role") == "tabpanel" and data.get("id"):
            self.panels[data["id"]] = data

if INDEX.is_file():
    parser = AuditParser()
    parser.feed(INDEX.read_text(encoding="utf-8"))
    duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        errors.append(f"duplicate HTML ids: {duplicates}")
    if parser.main is None or parser.main.get("tabindex") != "-1":
        errors.append("skip-link target #workspace must be programmatically focusable with tabindex=-1")
    if parser.progress is None or parser.progress.get("aria-labelledby") != "analysis-progress-label":
        errors.append("analysis progress must be labelled by #analysis-progress-label")
    if len(parser.tabs) != 6:
        errors.append(f"expected six result tabs, found {len(parser.tabs)}")
    for tab in parser.tabs:
        tab_id = tab.get("id", "")
        controls = tab.get("aria-controls", "")
        if not tab_id or not controls:
            errors.append("each result tab requires id and aria-controls")
            continue
        panel = parser.panels.get(controls)
        if panel is None:
            errors.append(f"tab {tab_id} controls missing panel {controls}")
        elif panel.get("aria-labelledby") != tab_id:
            errors.append(f"panel {controls} must be labelled by {tab_id}")

if STYLES.is_file():
    text = STYLES.read_text(encoding="utf-8")
    for required in (
        ".file-picker:focus-within",
        "[hidden] { display: none !important; }",
        ":focus-visible",
        "@media (max-width: 850px)",
        "@media (max-width: 560px)",
        "@media (prefers-reduced-motion: reduce)",
    ):
        if required not in text:
            errors.append(f"accessibility/responsive CSS invariant missing: {required}")

if APPLICATION.is_file():
    text = APPLICATION.read_text(encoding="utf-8")
    for required in (
        '["ArrowLeft", "ArrowRight", "Home", "End"]',
        "event.preventDefault();",
        'event.key === "Home"',
        'event.key === "End"',
    ):
        if required not in text:
            errors.append(f"result-tab keyboard invariant missing: {required}")

if RESULTS.is_file():
    text = RESULTS.read_text(encoding="utf-8")
    for required in (
        'wrapper.tabIndex = 0;',
        'wrapper.setAttribute("role", "region");',
        'Scrollable event-time abnormal return results table',
        'Scrollable prespecified robustness matrix',
    ):
        if required not in text:
            errors.append(f"scrollable-table accessibility invariant missing: {required}")

if STAGE7_TEST.is_file():
    text = STAGE7_TEST.read_text(encoding="utf-8")
    for required in (
        'TUTORIAL_CSV = path.resolve("../examples/efl_tutorial_synthetic.csv")',
        'page.keyboard.press("End")',
        'page.keyboard.press("Home")',
        'page.keyboard.press("ArrowRight")',
        'page.locator("#analysis-progress-wrap")).toBeHidden()',
        'page.locator("#result-panel-summary")).toBeVisible()',
        'page.locator("#result-panel-audits")).toBeHidden()',
        'Scrollable event-time abnormal return results table',
        'for (const width of [320, 390, 768, 1280])',
        'document.documentElement.scrollWidth - document.documentElement.clientWidth',
        'window.__EFL_STAGE6__.getResult() !== null',
    ):
        if required not in text:
            errors.append(f"Stage VII-E2 browser proof invariant missing: {required}")

if SPEC.is_file():
    text = SPEC.read_text(encoding="utf-8")
    for required in (
        "not a formal WCAG certification",
        "keyboard",
        "320",
        "1280",
        "assistive-technology",
        "scientific core",
    ):
        if required not in text:
            errors.append(f"Stage VII-E2 specification limitation/scope missing: {required}")

if errors:
    print("STAGE VII-E2 ACCESSIBILITY GATE: FAIL")
    for error in errors:
        print(" -", error)
    raise SystemExit(1)

print("STAGE VII-E2 ACCESSIBILITY GATE: PASS")
print(" - skip-link target and progress semantics: PASS")
print(" - result tab/panel relationships: PASS")
print(" - native hidden-state semantics: PASS")
print(" - keyboard tab navigation contract: PASS")
print(" - focus-visible file intake contract: PASS")
print(" - keyboard-scrollable result tables: PASS")
print(" - responsive browser proof contract: 320/390/768/1280 px")
