import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test, type APIRequestContext } from "@playwright/test";
import { exerciseD2RoundTrip } from "../tests/reproRoundTrip.js";

const BASE_PATH = "/empirical-finance-lab/";
const EXPECTED_ORIGIN = "https://mkhasan23.github.io";
const MANIFEST_SCHEMA = "efl-stage7-dist-manifest-1";
const EXPECTED_DOCUMENT_CSP = "default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; worker-src 'self'; frame-src 'none'; media-src 'none'; manifest-src 'self'; form-action 'self'";
const EXPECTED_BUILD_COMMIT = process.env.EFL_BUILD_COMMIT;
if (!EXPECTED_BUILD_COMMIT || !/^[0-9a-f]{40}$/.test(EXPECTED_BUILD_COMMIT)) {
  throw new Error("EFL_BUILD_COMMIT must be the exact deployed commit for the Stage VII live gate");
}

interface DistManifestFile {
  path: string;
  sha256: string;
  size: number;
}

interface DistManifest {
  artifact_root: string;
  file_count: number;
  files: DistManifestFile[];
  schema_version: string;
  total_bytes: number;
  tree_sha256: string;
}

const rawLiveUrl = process.env.EFL_STAGE7_LIVE_URL;
const manifestPath = process.env.EFL_STAGE7_MANIFEST;
if (!rawLiveUrl) {
  throw new Error("EFL_STAGE7_LIVE_URL is required for the deployed-site gate");
}
if (!manifestPath) {
  throw new Error("EFL_STAGE7_MANIFEST is required for the deployed-site gate");
}

const LIVE_URL = new URL(rawLiveUrl);
const manifest = JSON.parse(readFileSync(manifestPath, "utf8")) as DistManifest;

function validateManifest(): void {
  if (manifest.schema_version !== MANIFEST_SCHEMA || manifest.artifact_root !== "dist") {
    throw new Error("unexpected Stage VII dist-manifest authority");
  }
  if (!Array.isArray(manifest.files) || manifest.files.length === 0 || manifest.file_count !== manifest.files.length) {
    throw new Error("Stage VII dist-manifest file-count invariant failed");
  }
  if (!/^[a-f0-9]{64}$/.test(manifest.tree_sha256)) {
    throw new Error("Stage VII dist-manifest tree SHA-256 is malformed");
  }

  let totalBytes = 0;
  for (const entry of manifest.files) {
    if (
      typeof entry.path !== "string" ||
      entry.path === "" ||
      entry.path.startsWith("/") ||
      entry.path.split("/").includes("..") ||
      !Number.isInteger(entry.size) ||
      entry.size < 0 ||
      !/^[a-f0-9]{64}$/.test(entry.sha256)
    ) {
      throw new Error(`invalid Stage VII dist-manifest entry: ${JSON.stringify(entry)}`);
    }
    totalBytes += entry.size;
  }
  if (totalBytes !== manifest.total_bytes) {
    throw new Error("Stage VII dist-manifest total-bytes invariant failed");
  }

  const canonicalEntries = JSON.stringify(manifest.files);
  const treeSha = createHash("sha256").update(canonicalEntries, "utf8").digest("hex");
  if (treeSha !== manifest.tree_sha256) {
    throw new Error("Stage VII dist-manifest tree SHA-256 does not match its file entries");
  }
}

validateManifest();

async function liveArtifactState(request: APIRequestContext): Promise<string> {
  for (const entry of manifest.files) {
    const fileUrl = new URL(entry.path, LIVE_URL);
    if (fileUrl.origin !== EXPECTED_ORIGIN || !fileUrl.pathname.startsWith(BASE_PATH)) {
      return `URL_SCOPE_MISMATCH:${entry.path}`;
    }
    fileUrl.searchParams.set("efl-stage7-verify", manifest.tree_sha256);

    try {
      const response = await request.get(fileUrl.href, {
        headers: {
          "accept-encoding": "identity",
          "cache-control": "no-cache",
        },
        timeout: 30_000,
      });
      if (response.status() !== 200) {
        return `HTTP_${response.status()}:${entry.path}`;
      }
      const body = await response.body();
      if (body.byteLength !== entry.size) {
        return `SIZE_MISMATCH:${entry.path}:${body.byteLength}:${entry.size}`;
      }
      const sha256 = createHash("sha256").update(body).digest("hex");
      if (sha256 !== entry.sha256) {
        return `SHA256_MISMATCH:${entry.path}:${sha256}:${entry.sha256}`;
      }
    } catch (error) {
      return `REQUEST_ERROR:${entry.path}:${String(error)}`;
    }
  }
  return "PASS";
}

test("live GitHub Pages serves the exact tested Stage VII artifact", async ({ request }) => {
  expect(LIVE_URL.origin).toBe(EXPECTED_ORIGIN);
  expect(LIVE_URL.pathname).toBe(BASE_PATH);

  await expect
    .poll(() => liveArtifactState(request), {
      message: "live GitHub Pages bytes did not converge to the tested Stage VII artifact manifest",
      timeout: 120_000,
      intervals: [1_000, 2_000, 5_000, 10_000],
    })
    .toBe("PASS");
});

test("live GitHub Pages preserves pinned runtime parity, build provenance, document security, and analysis privacy", async ({ page }) => {
  await page.addInitScript(() => {
    const target = window as Window & { __EFL_STAGE7_CSP_VIOLATIONS__?: string[] };
    target.__EFL_STAGE7_CSP_VIOLATIONS__ = [];
    document.addEventListener("securitypolicyviolation", (event) => {
      target.__EFL_STAGE7_CSP_VIOLATIONS__?.push(`${event.effectiveDirective}:${event.blockedURI}`);
    });
  });

  const initializationRequests: Array<{ method: string; url: string }> = [];
  page.on("request", (request) => initializationRequests.push({ method: request.method(), url: request.url() }));

  const navigation = await page.goto(`./?efl-stage7-live=${manifest.tree_sha256}`, { waitUntil: "domcontentloaded" });
  expect(navigation?.status()).toBe(200);

  const pageUrl = new URL(page.url());
  expect(pageUrl.origin).toBe(EXPECTED_ORIGIN);
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

  for (const request of initializationRequests) {
    expect(["GET", "HEAD"]).toContain(request.method);
    const url = new URL(request.url);
    if (url.origin === EXPECTED_ORIGIN) {
      expect(url.pathname.startsWith(BASE_PATH), `same-origin live request escaped production base path: ${url}`).toBeTruthy();
    } else {
      expect(url.hostname, `unexpected live initialization origin: ${url}`).toBe("cdn.jsdelivr.net");
    }
  }
  expect(
    initializationRequests.some((request) => new URL(request.url).pathname === `${BASE_PATH}efl-core.json`),
    "authoritative scientific core was not fetched from the live production repository subpath",
  ).toBeTruthy();

  const analysisRequests: string[] = [];
  page.on("request", (request) => analysisRequests.push(request.url()));
  const parity = await page.evaluate(() => window.__EFL_STAGE5__.runFixture("KA-003"));
  expect(parity.mismatches).toEqual([]);
  expect(analysisRequests, "live production scientific analysis emitted a network request").toEqual([]);

  const repro = parity.result.reproducibility as Record<string, unknown>;
  const coreEnvironment = repro.environment as Record<string, unknown>;
  expect(coreEnvironment.build_commit).toBe(EXPECTED_BUILD_COMMIT);
  expect(repro.analysis_id).toMatch(/^[a-f0-9]{64}$/);
  expect(repro.execution_id).toMatch(/^[a-f0-9]{64}$/);

  const cspViolations = await page.evaluate(() => (
    (window as Window & { __EFL_STAGE7_CSP_VIOLATIONS__?: string[] }).__EFL_STAGE7_CSP_VIOLATIONS__ ?? []
  ));
  expect(cspViolations, "live production document emitted a CSP violation").toEqual([]);
});

test("live GitHub Pages closes the privacy-preserving reproducibility ZIP round trip", async ({ page }) => {
  const navigation = await page.goto(`./?efl-stage7-d2=${manifest.tree_sha256}`, { waitUntil: "domcontentloaded" });
  expect(navigation?.status()).toBe(200);
  await exerciseD2RoundTrip(page, EXPECTED_BUILD_COMMIT);
});
