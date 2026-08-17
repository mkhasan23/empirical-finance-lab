import { expect, test } from "@playwright/test";

const BASE_PATH = "/empirical-finance-lab/";
const EXPECTED_DOCUMENT_CSP = "default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self'; frame-src 'none'; media-src 'none'; manifest-src 'self'; form-action 'self'";

test("production Pages base path preserves pinned runtime parity, document security, and analysis privacy", async ({ page }) => {
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

  const cspViolations = await page.evaluate(() => (
    (window as Window & { __EFL_STAGE7_CSP_VIOLATIONS__?: string[] }).__EFL_STAGE7_CSP_VIOLATIONS__ ?? []
  ));
  expect(cspViolations, "production-like document emitted a CSP violation").toEqual([]);
});
