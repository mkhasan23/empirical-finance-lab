export type BundleContext = {
  result: Record<string, unknown>;
  originalUploadSha256: string;
  engineInputSha256: string;
  columnMapping: Record<string, string>;
  normalization: Record<string, unknown>;
  normalizedToOriginalSourceRow: number[];
  runtime: Record<string, unknown> | null;
};

type ZipEntry = { name: string; bytes: Uint8Array };

const encoder = new TextEncoder();

function u16(value: number): Uint8Array {
  const out = new Uint8Array(2);
  new DataView(out.buffer).setUint16(0, value, true);
  return out;
}

function u32(value: number): Uint8Array {
  const out = new Uint8Array(4);
  new DataView(out.buffer).setUint32(0, value >>> 0, true);
  return out;
}

function concat(parts: Uint8Array[]): Uint8Array {
  const total = parts.reduce((sum, part) => sum + part.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }
  return out;
}

let crcTable: Uint32Array | null = null;
function getCrcTable(): Uint32Array {
  if (crcTable) return crcTable;
  crcTable = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = (c & 1) !== 0 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    crcTable[n] = c >>> 0;
  }
  return crcTable;
}

export function crc32(bytes: Uint8Array): number {
  const table = getCrcTable();
  let crc = 0xFFFFFFFF;
  for (const byte of bytes) crc = table[(crc ^ byte) & 0xFF]! ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

export function createStoredZip(files: Record<string, string>): Uint8Array {
  const entries: ZipEntry[] = Object.entries(files)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([name, text]) => ({ name, bytes: encoder.encode(text) }));
  const localParts: Uint8Array[] = [];
  const centralParts: Uint8Array[] = [];
  let localOffset = 0;
  const utf8Flag = 0x0800;
  const dosTime = 0;
  const dosDate = 0x0021; // 1980-01-01, deterministic ZIP timestamp.

  for (const entry of entries) {
    const nameBytes = encoder.encode(entry.name);
    const crc = crc32(entry.bytes);
    const localHeader = concat([
      u32(0x04034B50), u16(20), u16(utf8Flag), u16(0), u16(dosTime), u16(dosDate),
      u32(crc), u32(entry.bytes.length), u32(entry.bytes.length), u16(nameBytes.length), u16(0), nameBytes,
    ]);
    localParts.push(localHeader, entry.bytes);

    const centralHeader = concat([
      u32(0x02014B50), u16(20), u16(20), u16(utf8Flag), u16(0), u16(dosTime), u16(dosDate),
      u32(crc), u32(entry.bytes.length), u32(entry.bytes.length), u16(nameBytes.length), u16(0), u16(0),
      u16(0), u16(0), u32(0), u32(localOffset), nameBytes,
    ]);
    centralParts.push(centralHeader);
    localOffset += localHeader.length + entry.bytes.length;
  }

  const central = concat(centralParts);
  const local = concat(localParts);
  const end = concat([
    u32(0x06054B50), u16(0), u16(0), u16(entries.length), u16(entries.length),
    u32(central.length), u32(local.length), u16(0),
  ]);
  return concat([local, central, end]);
}

function json(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function csvCell(value: unknown): string {
  const text = value === null || value === undefined ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function csvFromRows(headers: string[], rows: Record<string, unknown>[]): string {
  const lines = [headers.join(",")];
  for (const row of rows) lines.push(headers.map((header) => csvCell(row[header])).join(","));
  return `${lines.join("\n")}\n`;
}

function objectValue(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function arrayValue(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item)) : [];
}

export function buildReproducibilityFiles(context: BundleContext): Record<string, string> {
  const result = context.result;
  const coreRepro = objectValue(result.reproducibility);
  const coreHashes = objectValue(coreRepro.hashes);
  const primary = objectValue(result.primary);
  const classical = objectValue(primary.classical_inference);
  const permutation = objectValue(primary.permutation_inference);
  const eventRows = arrayValue(primary.event_time);
  const robustness = arrayValue(result.robustness);
  const placebo = objectValue(result.placebo);
  const audits = arrayValue(result.audits);
  const executionId = String(coreRepro.execution_id ?? "UNAVAILABLE");
  const analysisId = String(coreRepro.analysis_id ?? "UNAVAILABLE");
  const engineRawHash = String(coreHashes.raw_file_sha256 ?? context.engineInputSha256);
  const canonicalHash = String(coreHashes.canonical_data_sha256 ?? "UNAVAILABLE");
  const specHash = String(coreHashes.specification_sha256 ?? "UNAVAILABLE");

  const manifest = {
    bundle_schema: "EFL_REPRODUCIBILITY_BUNDLE_V1",
    software_version: coreRepro.software_version ?? "0.0.0",
    analysis_id: analysisId,
    execution_id: executionId,
    hashes: {
      raw_file_sha256: context.originalUploadSha256,
      engine_input_sha256: engineRawHash,
      canonical_data_sha256: canonicalHash,
      specification_sha256: specHash,
    },
    column_mapping: context.columnMapping,
    normalization: context.normalization,
    scientific_core_manifest: coreRepro,
  };

  const inference = {
    classical: Object.keys(classical).length > 0 ? classical : null,
    permutation: Object.keys(permutation).length > 0 ? permutation : null,
  };
  const placeboSummary = Object.keys(placebo).length > 0 ? {
    actual_car: placebo.actual_car,
    candidate_count: placebo.candidate_count,
    extreme_count: placebo.extreme_count,
    historical_placebo_tail_proportion: placebo.historical_placebo_tail_proportion,
    excluded_candidate_count: Array.isArray(placebo.excluded_candidates) ? placebo.excluded_candidates.length : 0,
  } : null;
  const placeboEvents = Array.isArray(placebo.candidate_dates) && Array.isArray(placebo.placebo_cars)
    ? placebo.candidate_dates.map((date, index) => ({ date, placebo_car: (placebo.placebo_cars as unknown[])[index] }))
    : [];
  const citation = [
    "Empirical Finance Lab: Audit-First Tools for Credible Empirical Finance Research.",
    "Author: Muhammad Kamrul Hasan.",
    `Software version: ${String(coreRepro.software_version ?? "0.0.0")}.`,
    "Repository: https://github.com/mkhasan23/empirical-finance-lab",
    "Pre-alpha software: no version-specific DOI has been assigned yet.",
    "If a future validated release materially contributes to your research, cite the exact released version and DOI provided with that release.",
    "",
  ].join("\n");
  const readme = [
    "Empirical Finance Lab reproducibility bundle",
    "===========================================",
    "",
    "This archive was generated locally in the browser. It does not include the proprietary/raw research file.",
    "manifest.json records the SHA-256 of the original local file and the transformed engine input separately.",
    "analysis_spec.json is the locked research specification sent to the validated Python core.",
    "normalization.json documents column mapping, any explicitly approved sort, and normalized-to-original source-row provenance.",
    "event_time.csv reports the event-window values returned by the scientific core; no econometric quantity is recomputed by the exporter.",
    "Referee Mode is a deterministic synthesis of version-controlled audit rules and is not causal certification.",
    "",
    `AnalysisID: ${analysisId}`,
    `ExecutionID: ${executionId}`,
    "",
  ].join("\n");

  return {
    "README.txt": readme,
    "analysis_spec.json": json(result.specification ?? null),
    "audit_report.json": json(audits),
    "citation.txt": citation,
    "data_audit.json": json({ audits, source_row_provenance: context.normalizedToOriginalSourceRow }),
    "environment.json": json({ core_environment: coreRepro.environment ?? null, browser_runtime: context.runtime }),
    "event_time.csv": csvFromRows(["date", "tau", "security_return", "benchmark_return", "expected_return", "abnormal_return", "cumulative_abnormal_return"], eventRows),
    "inference.json": json(inference),
    "manifest.json": json(manifest),
    "model_results.json": json(primary),
    "normalization.json": json({ column_mapping: context.columnMapping, normalization: context.normalization, normalized_to_original_source_row: context.normalizedToOriginalSourceRow }),
    "placebo_events.csv": csvFromRows(["date", "placebo_car"], placeboEvents),
    "placebo_summary.json": json(placeboSummary),
    "referee_report.md": String(result.referee_report ?? "# Empirical Finance Lab — Referee Mode\n\nNot available.\n"),
    "robustness.csv": csvFromRows(["model", "window", "car", "permutation_p_value", "permutation_ge_count", "B", "sign", "significant_5pct"], robustness.map((row) => ({ ...row, window: Array.isArray(row.window) ? row.window.join(":") : row.window }))),
  };
}

export function buildReproducibilityZip(context: BundleContext): { filename: string; bytes: Uint8Array } {
  const files = buildReproducibilityFiles(context);
  const repro = objectValue(context.result.reproducibility);
  const executionId = String(repro.execution_id ?? "unavailable").replace(/[^a-zA-Z0-9]/g, "").slice(0, 12) || "unavailable";
  return { filename: `efl-run-${executionId}.zip`, bytes: createStoredZip(files) };
}
