import { expect, test, type Page } from "@playwright/test";
import path from "node:path";
import { exerciseD2RoundTrip } from "./reproRoundTrip.js";

const BASE_PATH = "/empirical-finance-lab/";
const TUTORIAL_CSV = path.resolve("../examples/efl_tutorial_synthetic.csv");
const EXPECTED_DOCUMENT_CSP = "default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self'; frame-src 'none'; media-src 'none'; manifest-src 'self'; form-action 'self'";
const EXPECTED_BUILD_COMMIT = process.env.EFL_BUILD_COMMIT;
if (!EXPECTED_BUILD_COMMIT || !/^[0-9a-f]{40}$/.test(EXPECTED_BUILD_COMMIT)) {
  throw new Error("EFL_BUILD_COMMIT must be the exact 40-character candidate commit for the Stage VII production gate");
}

test("production Pages base path preserves pinned runtime parity, build provenance, document security, and analysis privacy", async ({ page }) => {
  await page.addInitScript(() => {
    const target = window as Window & { __EFL_STAGE7_CSP_VIOLATIONS__?: string[] };
    target.__EFL_STAGE7_CSP_VIOLATIONS__ = [];
    document.addEventListener("securitypolicyviolation", (event) => {
      target.__EFL_STAGE7_CSP_VIOLATIONS__?.push(`${event.effectiveDirective}:${event.blockedURI}`);
    });
  });

  const initializationRequests: Array<{ method: string; url: string }> = [];
  page.on("request", (request) => initializationRequests.push({ method: request.method(), url: request.url() }));

  await page.goto("./");
  const pageUrl = new URL(page.url());
  expect(pageUrl.pathname).toBe(BASE_PATH);
  expect(await page.evaluate(() => new URL(document.baseURI).pathname)).toBe(BASE_PATH);

  const documentSecurity = await page.evaluate(() => ({
    csp: document.querySelector<HTMLMetaElement>('meta[http-equiv="Content-Security-Policy"]')?.content ?? null,
    referrer: document.querySelector<HTMLMetaElement>('meta[name="referrer"]')?.content ?? null,
  }));
  expect(documentSecurity.csp).toBe(EXPECTED_DOCUMENT_CSP);
  expect(documentSecurity.referrer).toBe("no-referrer");

  const runtime = await page.evaluate(() => window.__EFL_STAGE5__.initialize());
  expect(runtime.pyodide_version).toBe("314.0.4");
  expect(runtime.python_version).toBe("3.14.2");
  expect(runtime.numpy_version).toBe("2.4.3");
  expect(runtime.scipy_version).toBe("1.18.0");
  expect(runtime.efl_version).toBe("0.0.0");
  expect(runtime.build_commit).toBe(EXPECTED_BUILD_COMMIT);
  expect(runtime.build_mode).toBe("github-pages");
  expect(runtime.build_source).toBe("github-actions");

  const pageOrigin = pageUrl.origin;
  for (const request of initializationRequests) {
    expect(["GET", "HEAD"]).toContain(request.method);
    const url = new URL(request.url);
    if (url.origin === pageOrigin) {
      expect(url.pathname.startsWith(BASE_PATH), `same-origin request escaped production base path: ${url}`).toBeTruthy();
    } else {
      expect(url.hostname, `unexpected initialization origin: ${url}`).toBe("cdn.jsdelivr.net");
    }
  }
  expect(
    initializationRequests.some((request) => new URL(request.url).pathname === `${BASE_PATH}efl-core.json`),
    "authoritative scientific core was not fetched from the production repository subpath",
  ).toBeTruthy();

  const analysisRequests: string[] = [];
  page.on("request", (request) => analysisRequests.push(request.url()));
  const parity = await page.evaluate(() => window.__EFL_STAGE5__.runFixture("KA-003"));
  expect(parity.mismatches).toEqual([]);
  expect(analysisRequests, "production-like scientific analysis emitted a network request").toEqual([]);

  const repro = parity.result.reproducibility as Record<string, unknown>;
  const coreEnvironment = repro.environment as Record<string, unknown>;
  expect(coreEnvironment.build_commit).toBe(EXPECTED_BUILD_COMMIT);
  expect(repro.analysis_id).toMatch(/^[a-f0-9]{64}$/);
  expect(repro.execution_id).toMatch(/^[a-f0-9]{64}$/);

  const cspViolations = await page.evaluate(() => (
    (window as Window & { __EFL_STAGE7_CSP_VIOLATIONS__?: string[] }).__EFL_STAGE7_CSP_VIOLATIONS__ ?? []
  ));
  expect(cspViolations, "production-like document emitted a CSP violation").toEqual([]);
});

test("production Pages candidate completes the privacy-preserving reproducibility ZIP round trip", async ({ page }) => {
  await page.goto("./");
  await exerciseD2RoundTrip(page, EXPECTED_BUILD_COMMIT);
});

async function completeTutorialAnalysis(page: Page): Promise<void> {
  await page.getByLabel("Choose CSV file").setInputFiles(TUTORIAL_CSV);
  await expect(page.getByRole("button", { name: "Continue to research specification" })).toBeEnabled();
  await page.getByRole("button", { name: "Continue to research specification" }).click();
  await page.getByLabel("Calendar announcement date").fill("2025-07-31");
  await page.getByLabel("Announcement timing").selectOption("during_or_before_market");
  await page.getByRole("button", { name: "Use suggestion" }).click();
  await page.getByLabel(/I confirm the effective event trading date/).check();
  await page.getByLabel("Estimation start (τ)").fill("-140");
  await page.getByLabel("Estimation end (τ)").fill("-20");
  await page.getByLabel("Event start (τ)").fill("-1");
  await page.getByLabel("Event end (τ)").fill("1");
  await page.getByLabel("Permutation count (B)").fill("1000");
  await page.getByLabel("PCG64 seed").fill("20260817");
  await page.getByLabel("Run historical pseudo-event placebo diagnostic").uncheck();
  await page.getByLabel(/Also run market-adjusted model/).uncheck();
  for (const id of ["robust-start-1", "robust-end-1", "robust-start-2", "robust-end-2"]) {
    await page.locator(`#${id}`).fill("");
  }
  await page.getByRole("button", { name: "Review & lock specification" }).click();
  await page.getByRole("button", { name: "Run locked analysis" }).click();
  await page.waitForFunction(() => window.__EFL_STAGE6__.getResult() !== null, undefined, { timeout: 300_000 });
  await expect(page.locator("#metric-state")).toHaveText("COMPLETE", { timeout: 300_000 });
  await expect(page.locator("#metric-car")).toHaveText("3.000%");
}

test("production candidate preserves keyboard semantics and completed-result responsiveness", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  await page.goto("./");

  const duplicateIds = await page.evaluate(() => {
    const ids = [...document.querySelectorAll<HTMLElement>("[id]")].map((node) => node.id);
    return ids.filter((id, index) => ids.indexOf(id) !== index);
  });
  expect(duplicateIds).toEqual([]);
  await expect(page.locator("#workspace")).toHaveAttribute("tabindex", "-1");
  await expect(page.locator("#analysis-progress")).toHaveAttribute("aria-labelledby", "analysis-progress-label");

  const skipLink = page.getByRole("link", { name: "Skip to analysis workspace" });
  await skipLink.focus();
  await expect(skipLink).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#workspace")).toBeFocused();

  const fileInput = page.getByLabel("Choose CSV file");
  await fileInput.focus();
  const pickerFocus = await page.locator(".file-picker").evaluate((node) => {
    const style = getComputedStyle(node);
    return { style: style.outlineStyle, width: style.outlineWidth };
  });
  expect(pickerFocus.style).not.toBe("none");
  expect(Number.parseFloat(pickerFocus.width)).toBeGreaterThan(0);

  await completeTutorialAnalysis(page);

  const relationships = await page.getByRole("tab").evaluateAll((tabs) => tabs.map((tab) => {
    const controls = tab.getAttribute("aria-controls");
    const panel = controls ? document.getElementById(controls) : null;
    return {
      tabId: tab.id,
      controls,
      panelLabelledBy: panel?.getAttribute("aria-labelledby") ?? null,
    };
  }));
  expect(relationships).toHaveLength(6);
  for (const relation of relationships) {
    expect(relation.tabId).not.toBe("");
    expect(relation.controls).not.toBeNull();
    expect(relation.panelLabelledBy).toBe(relation.tabId);
  }

  const mainTab = page.getByRole("tab", { name: "Main result" });
  await mainTab.focus();
  await page.keyboard.press("End");
  const reproduceTab = page.getByRole("tab", { name: "Reproduce & cite" });
  await expect(reproduceTab).toBeFocused();
  await expect(reproduceTab).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("Home");
  await expect(mainTab).toBeFocused();
  await page.keyboard.press("ArrowRight");
  const auditTab = page.getByRole("tab", { name: "Integrity audit" });
  await expect(auditTab).toBeFocused();
  await expect(auditTab).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("tabpanel", { name: "Integrity audit" })).toBeVisible();

  await mainTab.click();
  const tableRegion = page.getByRole("region", { name: "Scrollable event-time abnormal return results table" });
  await expect(tableRegion).toBeVisible();
  await tableRegion.focus();
  await expect(tableRegion).toBeFocused();
  const tableOverflow = await tableRegion.evaluate((node) => node.scrollWidth > node.clientWidth);
  expect(tableOverflow).toBeTruthy();

  for (const width of [320, 390, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow, `document overflow at ${width}px`).toBeLessThanOrEqual(1);
  }
});

