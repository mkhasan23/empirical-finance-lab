import { expect, test } from "@playwright/test";

const BASE_PATH = "/empirical-finance-lab/";

test("production Pages base path preserves pinned runtime parity and analysis privacy", async ({ page }) => {
  const initializationRequests: Array<{ method: string; url: string }> = [];
  page.on("request", (request) => initializationRequests.push({ method: request.method(), url: request.url() }));

  await page.goto("./");
  const pageUrl = new URL(page.url());
  expect(pageUrl.pathname).toBe(BASE_PATH);
  expect(await page.evaluate(() => new URL(document.baseURI).pathname)).toBe(BASE_PATH);

  const runtime = await page.evaluate(() => window.__EFL_STAGE5__.initialize());
  expect(runtime.pyodide_version).toBe("314.0.4");
  expect(runtime.python_version).toBe("3.14.2");
  expect(runtime.numpy_version).toBe("2.4.3");
  expect(runtime.scipy_version).toBe("1.18.0");
  expect(runtime.efl_version).toBe("0.0.0");

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
});
