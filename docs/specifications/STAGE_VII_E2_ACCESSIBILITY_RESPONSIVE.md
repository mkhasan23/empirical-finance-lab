# Stage VII-E2 — Accessibility, keyboard, and responsive validation

## Purpose

Stage VII-E2 hardens the existing Stage VI/VII browser application for keyboard and screen-reader semantics without changing any scientific computation, numerical authority, runtime dependency, analysis identity, or release provenance rule.

This tranche is intentionally narrow. It is **not a formal WCAG certification** and does not claim that independent assistive-technology user testing has been completed. Formal external accessibility review remains appropriate during Public Beta.

## Frozen boundaries

E2 does not modify the Python scientific core, validation corpus, Pyodide/runtime pins, watchdogs, AnalysisID/ExecutionID definitions, reproducibility semantics, CSP, or npm dependency graph. The validated scientific core remains the only authority for AR/CAR, inference, placebo, robustness, audit, and reproducibility quantities.

## Semantic and keyboard contract

The production document must preserve:

- a programmatically focusable `#workspace` skip-link target;
- an explicitly labelled analysis progress element;
- six result tabs with unique IDs, `aria-controls`, and matching tab panels labelled by their controlling tabs;
- native `hidden` state remains authoritative even when components define explicit `display` rules, so inactive tab panels and completed progress UI are not left in the rendered layout;
- automatic tab activation with Left/Right Arrow plus Home/End navigation;
- visible focus treatment for the visually customized local-file input;
- keyboard-focusable regions for horizontally scrollable result tables;
- existing reduced-motion behavior.

## Responsive proof

The production-like Chromium gate completes the deterministic E1 tutorial analysis, verifies that only the selected result panel remains rendered and that completed progress UI is hidden, and checks the rendered result at **320, 390, 768, and 1280 CSS pixels**. At each width, document-level horizontal overflow greater than one pixel is a gate failure. Wide result tables may overflow only inside their dedicated keyboard-focusable scroll regions.

The E2 browser proof also verifies that the tutorial still completes at CAR[-1,+1] = +3.000%; this is a regression anchor only and does not create a second scientific authority.

## Scope limitation

Automated DOM and Playwright checks can detect regressions in semantics, keyboard behavior, focus visibility, and viewport containment, but they cannot substitute for all manual accessibility evaluation. In particular, E2 does not certify conformance across every browser/assistive-technology combination, cognitive-accessibility need, zoom configuration, or operating-system high-contrast mode.

Independent assistive-technology and usability feedback should therefore remain part of Stage VIII Public Beta validation rather than being silently inferred from these automated tests.
