import { expect, test } from "@playwright/test";
import path from "node:path";

const KA003 = path.resolve("../validation/known_answer/KA-003/data.csv");
const FM001 = path.resolve("../validation/failure_modes/FM-001/data.csv");

async function configureKa003(page: import("@playwright/test").Page, options: { fullDiagnostics?: boolean } = {}) {
  await page.goto("/");
  await page.getByLabel("Choose CSV file").setInputFiles(KA003);
  await expect(page.getByText("Local intake checks completed", { exact: false })).toBeVisible();
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

  if (!options.fullDiagnostics) {
    await page.getByLabel("Run historical pseudo-event placebo diagnostic").uncheck();
    await page.getByLabel(/Also run market-adjusted model/).uncheck();
    await page.locator("#robust-start-1").fill("");
    await page.locator("#robust-end-1").fill("");
    await page.locator("#robust-start-2").fill("");
    await page.locator("#robust-end-2").fill("");
  }

  await page.getByRole("button", { name: "Review & lock specification" }).click();
  await expect(page.getByRole("heading", { name: "Locked analysis specification" })).toBeVisible();
}

test("researcher journey produces the known KA-003 CAR in the validated browser engine", async ({ page, browserName }) => {
  const requests: Array<{ method: string; url: string }> = [];
  page.on("request", (request) => requests.push({ method: request.method(), url: request.url() }));
  await configureKa003(page);
  await page.getByRole("button", { name: "Run locked analysis" }).click();
  await expect(page.locator("#metric-state")).toHaveText("COMPLETE", { timeout: 300_000 });
  await expect(page.locator("#metric-car")).toHaveText("3.000%");
  await expect(page.locator("#metric-model")).toHaveText("market model");
  await expect(page.getByRole("tab", { name: "Integrity audit" })).toBeVisible();
  expect(requests.every((request) => ["GET", "HEAD"].includes(request.method))).toBe(true);
  for (const request of requests) {
    const url = new URL(request.url);
    expect(url.origin === new URL(page.url()).origin || url.hostname === "cdn.jsdelivr.net", `${browserName} unexpected request ${request.url}`).toBeTruthy();
  }
});

test("Chromium renders robustness, placebo, Referee Mode, and downloads a reproducibility ZIP", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "extended Stage VI workflow is exercised once in Chromium");
  await configureKa003(page, { fullDiagnostics: true });
  await page.getByRole("button", { name: "Run locked analysis" }).click();
  await expect(page.locator("#metric-state")).toHaveText("COMPLETE", { timeout: 300_000 });

  await page.getByRole("tab", { name: "Robustness" }).click();
  await expect(page.getByRole("table", { name: "Prespecified robustness matrix" })).toBeVisible();
  await page.getByRole("tab", { name: "Placebo" }).click();
  await expect(page.getByText("Historical pseudo-event diagnostic")).toBeVisible();
  await page.getByRole("tab", { name: "Referee Mode" }).click();
  await expect(page.getByText("Causal interpretation: NOT ESTABLISHED")).toBeVisible();

  await page.getByRole("tab", { name: "Reproduce & cite" }).click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Download reproducibility bundle/ }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^efl-run-[a-zA-Z0-9]+\.zip$/);
});

test("duplicate dates are blocked during local intake before specification", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "input failure UX is exercised once in Chromium");
  await page.goto("/");
  await page.getByLabel("Choose CSV file").setInputFiles(FM001);
  await expect(page.getByText("DATA_DUPLICATE_DATE")).toBeVisible();
  await expect(page.getByRole("button", { name: "Continue to research specification" })).toBeDisabled();
});

test("mobile layout retains a keyboard- and label-addressable workflow", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "responsive accessibility smoke is exercised once in Chromium");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Audit-First Event Study Analyzer" })).toBeVisible();
  await expect(page.getByLabel("Choose CSV file")).toBeVisible();
  await expect(page.getByLabel("Return units")).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});
