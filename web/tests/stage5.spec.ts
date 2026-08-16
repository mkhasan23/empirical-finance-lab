import { expect, test } from "@playwright/test";

const FULL_PARITY_CASES = ["KA-003", "INF-001", "PLC-001", "ROB-001", "FM-001"];

test("pinned runtime preserves scientific parity without analysis-time network transmission", async ({ page, browserName }) => {
  const initializationRequests: Array<{ method: string; url: string }> = [];
  page.on("request", (request) => initializationRequests.push({ method: request.method(), url: request.url() }));

  await page.goto("/");
  const runtime = await page.evaluate(() => window.__EFL_STAGE5__.initialize());
  expect(runtime.pyodide_version).toBe("314.0.4");
  expect(runtime.python_version).toBe("3.14.2");
  expect(runtime.numpy_version).toBe("2.4.3");
  expect(runtime.scipy_version).toBe("1.18.0");
  expect(runtime.efl_version).toBe("0.0.0");

  for (const request of initializationRequests) {
    expect(["GET", "HEAD"]).toContain(request.method);
    const url = new URL(request.url);
    expect(url.origin === new URL(page.url()).origin || url.hostname === "cdn.jsdelivr.net").toBeTruthy();
  }

  const analysisRequests: string[] = [];
  page.on("request", (request) => analysisRequests.push(request.url()));
  const cases = browserName === "chromium" ? FULL_PARITY_CASES : ["KA-003"];
  for (const fixture of cases) {
    const result = await page.evaluate((id) => window.__EFL_STAGE5__.runFixture(id), fixture);
    expect(result.mismatches, `${browserName} ${fixture} parity mismatch`).toEqual([]);
  }
  expect(analysisRequests, `${browserName} emitted a network request during scientific analysis`).toEqual([]);
});

test("cancellation destroys the live worker and requires clean reinitialization", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "real cancellation lifecycle is exercised once in Chromium");
  await page.goto("/");
  await page.evaluate(() => window.__EFL_STAGE5__.initialize());
  const cancellation = await page.evaluate(async () => {
    const api = window.__EFL_STAGE5__;
    const run = api.runFixture("KA-003")
      .then(() => ({ resolved: true, code: null as string | null }))
      .catch((error: unknown) => ({
        resolved: false,
        code: typeof error === "object" && error !== null && "code" in error ? String((error as { code: unknown }).code) : null,
      }));
    while (api.getState() !== "RUNNING") await new Promise((resolve) => setTimeout(resolve, 0));
    api.cancel();
    return run;
  });
  expect(cancellation).toEqual({ resolved: false, code: "CANCELLED" });
  expect(await page.evaluate(() => window.__EFL_STAGE5__.getState())).toBe("CANCELLED");

  const runtime = await page.evaluate(() => window.__EFL_STAGE5__.initialize());
  expect(runtime.pyodide_version).toBe("314.0.4");
  const rerun = await page.evaluate(() => window.__EFL_STAGE5__.runFixture("KA-003"));
  expect(rerun.mismatches).toEqual([]);
});
