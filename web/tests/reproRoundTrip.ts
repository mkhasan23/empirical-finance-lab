import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { expect, type Download, type Page } from "@playwright/test";

const KA003 = path.resolve("../validation/known_answer/KA-003/data.csv");
const EXPECTED_PAYLOADS = [
  "README.txt",
  "analysis_spec.json",
  "audit_report.json",
  "citation.txt",
  "data_audit.json",
  "environment.json",
  "event_time.csv",
  "inference.json",
  "model_results.json",
  "normalization.json",
  "placebo_events.csv",
  "placebo_summary.json",
  "referee_report.md",
  "robustness.csv",
  "scientific_result.json",
].sort();

function sha256(data: Uint8Array | string): string {
  return createHash("sha256").update(data).digest("hex");
}

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(value as Record<string, unknown>).sort()) out[key] = canonicalize((value as Record<string, unknown>)[key]);
    return out;
  }
  return value;
}

function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

function readU16(bytes: Uint8Array, offset: number): number {
  return new DataView(bytes.buffer, bytes.byteOffset + offset, 2).getUint16(0, true);
}

function readU32(bytes: Uint8Array, offset: number): number {
  return new DataView(bytes.buffer, bytes.byteOffset + offset, 4).getUint32(0, true);
}

function readEflStoredZip(bytes: Uint8Array): Record<string, Uint8Array> {
  if (bytes.length < 22) throw new Error("D2_ZIP_TOO_SHORT");
  const eocd = bytes.length - 22;
  if (readU32(bytes, eocd) !== 0x06054B50) throw new Error("D2_ZIP_EOCD_MISSING");
  const centralOffset = readU32(bytes, eocd + 16);
  const centralSize = readU32(bytes, eocd + 12);
  const entryCount = readU16(bytes, eocd + 10);
  if (readU16(bytes, eocd + 20) !== 0 || centralOffset + centralSize !== eocd) throw new Error("D2_ZIP_EOCD_INVALID");

  const decoder = new TextDecoder("utf-8", { fatal: true });
  const files: Record<string, Uint8Array> = {};
  let offset = 0;
  for (let index = 0; index < entryCount; index += 1) {
    if (readU32(bytes, offset) !== 0x04034B50) throw new Error("D2_ZIP_LOCAL_HEADER_INVALID");
    const flags = readU16(bytes, offset + 6);
    const method = readU16(bytes, offset + 8);
    const compressedSize = readU32(bytes, offset + 18);
    const uncompressedSize = readU32(bytes, offset + 22);
    const nameLength = readU16(bytes, offset + 26);
    const extraLength = readU16(bytes, offset + 28);
    if (flags !== 0x0800 || method !== 0 || compressedSize !== uncompressedSize || extraLength !== 0) throw new Error("D2_ZIP_FORMAT_INVALID");
    const name = decoder.decode(bytes.subarray(offset + 30, offset + 30 + nameLength));
    if (!name || name.startsWith("/") || name.includes("\\") || name.split("/").includes("..") || files[name]) throw new Error("D2_ZIP_PATH_INVALID");
    const dataOffset = offset + 30 + nameLength;
    const dataEnd = dataOffset + compressedSize;
    if (dataEnd > centralOffset) throw new Error("D2_ZIP_DATA_BOUNDARY_INVALID");
    files[name] = bytes.slice(dataOffset, dataEnd);
    offset = dataEnd;
  }
  if (offset !== centralOffset) throw new Error("D2_ZIP_LOCAL_REGION_INVALID");
  return files;
}

function textFile(files: Record<string, Uint8Array>, name: string): string {
  const bytes = files[name];
  if (!bytes) throw new Error(`D2_FILE_MISSING:${name}`);
  return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
}

function parseCsv(text: string): { headers: string[]; rows: string[][] } {
  const source = text.replace(/^\uFEFF/, "");
  const records: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i];
    if (quoted) {
      if (ch === '"') {
        if (source[i + 1] === '"') { field += '"'; i += 1; }
        else quoted = false;
      } else field += ch;
      continue;
    }
    if (ch === '"' && field.length === 0) quoted = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && source[i + 1] === "\n") i += 1;
      row.push(field); records.push(row); row = []; field = "";
    } else field += ch;
  }
  if (field.length > 0 || row.length > 0) { row.push(field); records.push(row); }
  while (records.length > 0 && records.at(-1)!.every((value) => value === "")) records.pop();
  return { headers: records[0] ?? [], rows: records.slice(1) };
}

function csvEscape(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

function reconstructEngineInput(
  originalText: string,
  mapping: Record<string, unknown>,
  sortApproved: boolean,
): { csvText: string; provenance: number[] } {
  const parsed = parseCsv(originalText);
  const di = parsed.headers.indexOf(String(mapping.date));
  const si = parsed.headers.indexOf(String(mapping.security_return));
  const bi = parsed.headers.indexOf(String(mapping.benchmark_return));
  if ([di, si, bi].some((index) => index < 0)) throw new Error("D2_MAPPING_INVALID");
  let rows = parsed.rows.map((record, index) => ({
    date: (record[di] ?? "").trim(),
    security: (record[si] ?? "").trim(),
    benchmark: (record[bi] ?? "").trim(),
    sourceRow: index + 2,
  }));
  const unsorted = rows.some((row, index) => index > 0 && rows[index - 1]!.date >= row.date);
  if (unsorted && !sortApproved) throw new Error("D2_SORT_APPROVAL_REQUIRED");
  if (unsorted && sortApproved) rows = rows.slice().sort((a, b) => a.date.localeCompare(b.date));
  const lines = ["date,security_return,benchmark_return"];
  for (const row of rows) lines.push([row.date, row.security, row.benchmark].map(csvEscape).join(","));
  return { csvText: `${lines.join("\n")}\n`, provenance: rows.map((row) => row.sourceRow) };
}

type VerifiedBundle = {
  manifest: Record<string, any>;
  specification: Record<string, unknown>;
  scientificResult: Record<string, unknown>;
};

function verifyBundle(zip: Uint8Array, original: Uint8Array): VerifiedBundle {
  const files = readEflStoredZip(zip);
  expect(Object.keys(files).sort()).toEqual(["manifest.json", ...EXPECTED_PAYLOADS].sort());
  const manifest = JSON.parse(textFile(files, "manifest.json")) as Record<string, any>;
  expect(manifest.bundle_schema).toBe("EFL_REPRODUCIBILITY_BUNDLE_V2");
  expect(manifest.reproduction_contract).toEqual({
    original_local_file_required: true,
    raw_research_data_included: false,
    deterministic_reexport_required: true,
  });
  expect(manifest.payload_integrity.algorithm).toBe("SHA-256");
  const entries = manifest.payload_integrity.files as Array<{ path: string; sha256: string; size: number }>;
  expect(entries.map((entry) => entry.path)).toEqual(EXPECTED_PAYLOADS);
  for (const entry of entries) {
    const payload = files[entry.path]!;
    expect(payload.byteLength).toBe(entry.size);
    expect(sha256(payload)).toBe(entry.sha256);
  }
  expect(sha256(canonicalJson(entries))).toBe(manifest.payload_integrity.tree_sha256);
  expect(sha256(original)).toBe(manifest.hashes.raw_file_sha256);

  const normalization = JSON.parse(textFile(files, "normalization.json")) as Record<string, any>;
  const originalText = new TextDecoder("utf-8", { fatal: true }).decode(original);
  const reconstructed = reconstructEngineInput(originalText, manifest.column_mapping, manifest.normalization.sorted_ascending_with_explicit_approval === true);
  expect(reconstructed.provenance).toEqual(normalization.normalized_to_original_source_row);
  expect(sha256(reconstructed.csvText)).toBe(manifest.hashes.engine_input_sha256);

  const specification = JSON.parse(textFile(files, "analysis_spec.json")) as Record<string, unknown>;
  const scientificResult = JSON.parse(textFile(files, "scientific_result.json")) as Record<string, unknown>;
  const repro = scientificResult.reproducibility as Record<string, any>;
  expect(scientificResult.state).toBe("COMPLETE");
  expect(scientificResult.specification).toEqual(specification);
  expect(repro.analysis_id).toBe(manifest.analysis_id);
  expect(repro.execution_id).toBe(manifest.execution_id);
  expect(repro.hashes.raw_file_sha256).toBe(manifest.hashes.engine_input_sha256);
  expect(repro.hashes.canonical_data_sha256).toBe(manifest.hashes.canonical_data_sha256);
  expect(repro.hashes.specification_sha256).toBe(manifest.hashes.specification_sha256);
  expect(repro.environment.build_commit).toBe(manifest.build_provenance.build_commit);
  expect(sha256(canonicalJson(scientificResult))).toBe(manifest.scientific_result_sha256);
  return { manifest, specification, scientificResult };
}

function compareReproducedResult(verified: VerifiedBundle, result: Record<string, unknown>): void {
  const repro = result.reproducibility as Record<string, any>;
  expect(repro.analysis_id).toBe(verified.manifest.analysis_id);
  expect(repro.execution_id).toBe(verified.manifest.execution_id);
  expect(repro.hashes.raw_file_sha256).toBe(verified.manifest.hashes.engine_input_sha256);
  expect(repro.hashes.canonical_data_sha256).toBe(verified.manifest.hashes.canonical_data_sha256);
  expect(repro.hashes.specification_sha256).toBe(verified.manifest.hashes.specification_sha256);
  expect(repro.environment.build_commit).toBe(verified.manifest.build_provenance.build_commit);
  expect(sha256(canonicalJson(result))).toBe(verified.manifest.scientific_result_sha256);
}

async function downloadBytes(download: Download): Promise<Uint8Array> {
  const saved = await download.path();
  if (!saved) throw new Error("D2_DOWNLOAD_PATH_UNAVAILABLE");
  return new Uint8Array(await readFile(saved));
}

async function setChecked(page: Page, id: string, checked: boolean): Promise<void> {
  const locator = page.locator(`#${id}`);
  if (checked) await locator.check();
  else await locator.uncheck();
}

async function configureFirstKa003Run(page: Page): Promise<void> {
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
  await page.getByLabel("Run historical pseudo-event placebo diagnostic").uncheck();
  await page.getByLabel(/Also run market-adjusted model/).uncheck();
  for (let index = 1; index <= 3; index += 1) {
    await page.locator(`#robust-start-${index}`).fill("");
    await page.locator(`#robust-end-${index}`).fill("");
  }
  await page.getByRole("button", { name: "Review & lock specification" }).click();
}

async function configureFromArchivedSpecification(page: Page, specification: Record<string, unknown>): Promise<void> {
  const estimation = specification.estimation_window as Record<string, unknown>;
  const eventWindow = specification.event_window as Record<string, unknown>;
  const inference = specification.inference as Record<string, unknown>;
  const placebo = specification.placebo as Record<string, unknown>;
  const robustnessModels = Array.isArray(specification.robustness_models) ? specification.robustness_models.map(String) : [];
  const robustnessWindows = Array.isArray(specification.robustness_windows) ? specification.robustness_windows as Record<string, unknown>[] : [];
  const excludedDates = Array.isArray(specification.excluded_dates) ? specification.excluded_dates.map(String) : [];

  expect(await page.locator("#return-units").inputValue()).toBe(String(specification.return_units));
  await page.getByLabel("Calendar announcement date").fill(String(specification.calendar_event_date));
  await page.getByLabel("Announcement timing").selectOption(String(specification.event_timing));
  await page.getByLabel("Effective event trading date", { exact: true }).fill(String(specification.effective_event_date));
  await page.getByLabel(/I confirm the effective event trading date/).check();
  await page.getByLabel("Estimation start (τ)").fill(String(estimation.start));
  await page.getByLabel("Estimation end (τ)").fill(String(estimation.end));
  await page.getByLabel("Event start (τ)").fill(String(eventWindow.start));
  await page.getByLabel("Event end (τ)").fill(String(eventWindow.end));
  await page.getByLabel("Expected-return model").selectOption(String(specification.model));
  await page.getByLabel("Hypothesis direction").selectOption(String(inference.direction));
  await page.getByLabel("Permutation count (B)").fill(String(inference.permutation_B));
  await page.getByLabel("PCG64 seed").fill(String(inference.seed));
  if (String(inference.direction) !== "two_sided") await setChecked(page, "one-sided-prespecified", true);
  await setChecked(page, "placebo-enabled", placebo.enabled === true);
  await setChecked(page, "alternative-model", robustnessModels.length > 0);
  await page.locator("#excluded-dates").fill(excludedDates.join(", "));
  for (let index = 1; index <= 3; index += 1) {
    const window = robustnessWindows[index - 1];
    await page.locator(`#robust-start-${index}`).fill(window ? String(window.start) : "");
    await page.locator(`#robust-end-${index}`).fill(window ? String(window.end) : "");
  }
  await page.getByRole("button", { name: "Review & lock specification" }).click();
}

async function runAndDownload(page: Page): Promise<{ result: Record<string, unknown>; zip: Uint8Array }> {
  await page.getByRole("button", { name: "Run locked analysis" }).click();
  await page.waitForFunction(() => window.__EFL_STAGE6__.getResult() !== null, undefined, { timeout: 300_000 });
  await expect(page.locator("#metric-state")).toHaveText("COMPLETE", { timeout: 300_000 });
  const result = await page.evaluate(() => window.__EFL_STAGE6__.getResult()) as Record<string, unknown>;
  await page.getByRole("tab", { name: "Reproduce & cite" }).click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Download reproducibility bundle/ }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^efl-run-[a-zA-Z0-9]+\.zip$/);
  return { result, zip: await downloadBytes(download) };
}

export async function exerciseD2RoundTrip(page: Page, expectedBuildCommit: string): Promise<void> {
  await configureFirstKa003Run(page);
  const first = await runAndDownload(page);
  const originalBytes = new Uint8Array(await readFile(KA003));
  const verified = verifyBundle(first.zip, originalBytes);
  compareReproducedResult(verified, first.result);
  expect(verified.manifest.build_provenance.build_commit).toBe(expectedBuildCommit);
  expect(verified.manifest.payload_integrity.files).toHaveLength(15);

  await page.locator("#new-run").click();
  await configureFromArchivedSpecification(page, verified.specification);
  const relocked = await page.evaluate(() => window.__EFL_STAGE6__.getLockedSpecification());
  expect(relocked).toEqual({ ...verified.specification, robustness_models: verified.specification.robustness_models ?? [] });

  const rerunRequests: string[] = [];
  page.on("request", (request) => rerunRequests.push(request.url()));
  const second = await runAndDownload(page);
  expect(rerunRequests, "D2 reproduction rerun emitted a network request after the runtime was already initialized").toEqual([]);
  compareReproducedResult(verified, second.result);
  expect([...second.zip]).toEqual([...first.zip]);
}
