import { normalizeMappedCsv, parseCsv, type ColumnMapping } from "./csvIntake";
import { readStoredZip, type StoredZipFiles } from "./storedZip";

const decoder = new TextDecoder("utf-8", { fatal: true });
const encoder = new TextEncoder();

export const REPRO_BUNDLE_SCHEMA = "EFL_REPRODUCIBILITY_BUNDLE_V2";
export const REPRO_PAYLOAD_PATHS = [
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
] as const;

type PayloadEntry = { path: string; sha256: string; size: number };

type ReproManifest = {
  bundle_schema: string;
  software_version: unknown;
  analysis_id: string;
  execution_id: string;
  build_provenance: Record<string, unknown>;
  hashes: {
    raw_file_sha256: string;
    engine_input_sha256: string;
    canonical_data_sha256: string;
    specification_sha256: string;
  };
  column_mapping: Record<string, unknown>;
  normalization: Record<string, unknown>;
  scientific_core_manifest: Record<string, unknown>;
  scientific_result_sha256: string;
  reproduction_contract: {
    original_local_file_required: boolean;
    raw_research_data_included: boolean;
    deterministic_reexport_required: boolean;
  };
  payload_integrity: {
    algorithm: string;
    files: PayloadEntry[];
    tree_sha256: string;
  };
};

export type VerifiedReproductionInputs = {
  manifest: ReproManifest;
  specification: Record<string, unknown>;
  scientificResult: Record<string, unknown>;
  normalizedCsvText: string;
  sourceRowProvenance: number[];
};

function rotr(value: number, shift: number): number {
  return (value >>> shift) | (value << (32 - shift));
}

const SHA256_K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]);

export function sha256HexSync(input: Uint8Array | string): string {
  const bytes = typeof input === "string" ? encoder.encode(input) : input;
  const bitLength = BigInt(bytes.length) * 8n;
  const paddedLength = Math.ceil((bytes.length + 9) / 64) * 64;
  const padded = new Uint8Array(paddedLength);
  padded.set(bytes);
  padded[bytes.length] = 0x80;
  const view = new DataView(padded.buffer);
  view.setUint32(paddedLength - 8, Number((bitLength >> 32n) & 0xFFFFFFFFn), false);
  view.setUint32(paddedLength - 4, Number(bitLength & 0xFFFFFFFFn), false);

  const h = new Uint32Array([
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ]);
  const w = new Uint32Array(64);
  for (let offset = 0; offset < paddedLength; offset += 64) {
    for (let i = 0; i < 16; i += 1) w[i] = view.getUint32(offset + i * 4, false);
    for (let i = 16; i < 64; i += 1) {
      const x = w[i - 15]!;
      const y = w[i - 2]!;
      const s0 = rotr(x, 7) ^ rotr(x, 18) ^ (x >>> 3);
      const s1 = rotr(y, 17) ^ rotr(y, 19) ^ (y >>> 10);
      w[i] = (w[i - 16]! + s0 + w[i - 7]! + s1) >>> 0;
    }
    let a = h[0]!; let b = h[1]!; let c = h[2]!; let d = h[3]!;
    let e = h[4]!; let f = h[5]!; let g = h[6]!; let hh = h[7]!;
    for (let i = 0; i < 64; i += 1) {
      const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (hh + S1 + ch + SHA256_K[i]! + w[i]!) >>> 0;
      const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (S0 + maj) >>> 0;
      hh = g; g = f; f = e; e = (d + temp1) >>> 0;
      d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }
    h[0] = (h[0]! + a) >>> 0; h[1] = (h[1]! + b) >>> 0;
    h[2] = (h[2]! + c) >>> 0; h[3] = (h[3]! + d) >>> 0;
    h[4] = (h[4]! + e) >>> 0; h[5] = (h[5]! + f) >>> 0;
    h[6] = (h[6]! + g) >>> 0; h[7] = (h[7]! + hh) >>> 0;
  }
  return [...h].map((value) => value.toString(16).padStart(8, "0")).join("");
}

function sortJson(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortJson);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(value as Record<string, unknown>).sort()) out[key] = sortJson((value as Record<string, unknown>)[key]);
    return out;
  }
  if (typeof value === "number" && !Number.isFinite(value)) throw new Error("REPRO_NONFINITE_JSON");
  return value;
}

export function canonicalJsonText(value: unknown): string {
  return JSON.stringify(sortJson(value));
}

function lexicalCompare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

export function buildPayloadIntegrity(files: Record<string, string>): { files: PayloadEntry[]; tree_sha256: string } {
  const entries = Object.entries(files)
    .sort(([a], [b]) => lexicalCompare(a, b))
    .map(([path, text]) => ({ path, sha256: sha256HexSync(text), size: encoder.encode(text).length }));
  return { files: entries, tree_sha256: sha256HexSync(canonicalJsonText(entries)) };
}

function parseJsonFile(files: StoredZipFiles, path: string): Record<string, unknown> {
  const bytes = files[path];
  if (!bytes) throw new Error(`REPRO_FILE_MISSING:${path}`);
  let text: string;
  try {
    text = decoder.decode(bytes);
  } catch {
    throw new Error(`REPRO_UTF8_INVALID:${path}`);
  }
  const value = JSON.parse(text) as unknown;
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`REPRO_JSON_OBJECT_REQUIRED:${path}`);
  return value as Record<string, unknown>;
}

function requireSha(value: unknown, label: string): string {
  const text = String(value ?? "");
  if (!/^[a-f0-9]{64}$/.test(text)) throw new Error(`REPRO_SHA256_INVALID:${label}`);
  return text;
}

function requireString(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) throw new Error(`REPRO_STRING_INVALID:${label}`);
  return value;
}

function arraysEqual(a: unknown[], b: unknown[]): boolean {
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

export function verifyReproducibilityArchive(bytes: Uint8Array): {
  files: StoredZipFiles;
  manifest: ReproManifest;
  specification: Record<string, unknown>;
  scientificResult: Record<string, unknown>;
} {
  const files = readStoredZip(bytes);
  const actualPaths = Object.keys(files).sort(lexicalCompare);
  const expectedPaths = ["manifest.json", ...REPRO_PAYLOAD_PATHS].sort(lexicalCompare);
  if (!arraysEqual(actualPaths, expectedPaths)) throw new Error("REPRO_PAYLOAD_SET_MISMATCH");

  const manifestRaw = parseJsonFile(files, "manifest.json");
  if (manifestRaw.bundle_schema !== REPRO_BUNDLE_SCHEMA) throw new Error("REPRO_BUNDLE_SCHEMA_UNSUPPORTED");
  const integrityRaw = manifestRaw.payload_integrity;
  if (!integrityRaw || typeof integrityRaw !== "object" || Array.isArray(integrityRaw)) throw new Error("REPRO_INTEGRITY_MISSING");
  const integrity = integrityRaw as Record<string, unknown>;
  if (integrity.algorithm !== "SHA-256") throw new Error("REPRO_INTEGRITY_ALGORITHM_UNSUPPORTED");
  if (!Array.isArray(integrity.files)) throw new Error("REPRO_INTEGRITY_FILE_LIST_INVALID");
  const declared = integrity.files.map((entry, index) => {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) throw new Error(`REPRO_INTEGRITY_ENTRY_INVALID:${index}`);
    const row = entry as Record<string, unknown>;
    const path = requireString(row.path, `payload.path.${index}`);
    const sha256 = requireSha(row.sha256, `payload.sha256.${path}`);
    const size = row.size;
    if (!Number.isInteger(size) || Number(size) < 0) throw new Error(`REPRO_PAYLOAD_SIZE_INVALID:${path}`);
    return { path, sha256, size: Number(size) };
  });
  if (!arraysEqual(declared.map((entry) => entry.path), [...REPRO_PAYLOAD_PATHS].sort(lexicalCompare))) {
    throw new Error("REPRO_INTEGRITY_PATH_LIST_MISMATCH");
  }
  const actualPayloadText: Record<string, string> = {};
  for (const entry of declared) {
    const payload = files[entry.path];
    if (!payload) throw new Error(`REPRO_FILE_MISSING:${entry.path}`);
    if (payload.length !== entry.size) throw new Error(`REPRO_PAYLOAD_SIZE_MISMATCH:${entry.path}`);
    if (sha256HexSync(payload) !== entry.sha256) throw new Error(`REPRO_PAYLOAD_SHA256_MISMATCH:${entry.path}`);
    try {
      actualPayloadText[entry.path] = decoder.decode(payload);
    } catch {
      throw new Error(`REPRO_UTF8_INVALID:${entry.path}`);
    }
  }
  const recomputed = buildPayloadIntegrity(actualPayloadText);
  const declaredTree = requireSha(integrity.tree_sha256, "payload.tree");
  if (recomputed.tree_sha256 !== declaredTree || canonicalJsonText(recomputed.files) !== canonicalJsonText(declared)) {
    throw new Error("REPRO_PAYLOAD_TREE_MISMATCH");
  }

  const hashes = manifestRaw.hashes;
  if (!hashes || typeof hashes !== "object" || Array.isArray(hashes)) throw new Error("REPRO_HASHES_MISSING");
  const hashMap = hashes as Record<string, unknown>;
  const manifest = manifestRaw as unknown as ReproManifest;
  requireSha(hashMap.raw_file_sha256, "original-file");
  requireSha(hashMap.engine_input_sha256, "engine-input");
  requireSha(hashMap.canonical_data_sha256, "canonical-data");
  requireSha(hashMap.specification_sha256, "specification");
  requireSha(manifestRaw.scientific_result_sha256, "scientific-result");
  requireSha(manifestRaw.analysis_id, "analysis-id");
  requireSha(manifestRaw.execution_id, "execution-id");

  const contract = manifestRaw.reproduction_contract;
  if (!contract || typeof contract !== "object" || Array.isArray(contract)) throw new Error("REPRO_CONTRACT_MISSING");
  const contractMap = contract as Record<string, unknown>;
  if (contractMap.original_local_file_required !== true || contractMap.raw_research_data_included !== false || contractMap.deterministic_reexport_required !== true) {
    throw new Error("REPRO_CONTRACT_INVALID");
  }
  const normalization = manifestRaw.normalization;
  if (!normalization || typeof normalization !== "object" || Array.isArray(normalization)) throw new Error("REPRO_NORMALIZATION_MISSING");
  if ((normalization as Record<string, unknown>).proprietary_raw_data_included !== false) throw new Error("REPRO_RAW_DATA_POLICY_INVALID");

  const specification = parseJsonFile(files, "analysis_spec.json");
  const scientificResult = parseJsonFile(files, "scientific_result.json");
  if (scientificResult.state !== "COMPLETE") throw new Error("REPRO_SCIENTIFIC_RESULT_NOT_COMPLETE");
  if (sha256HexSync(canonicalJsonText(scientificResult)) !== manifest.scientific_result_sha256) throw new Error("REPRO_SCIENTIFIC_RESULT_HASH_MISMATCH");
  if (canonicalJsonText(scientificResult.specification) !== canonicalJsonText(specification)) throw new Error("REPRO_SPECIFICATION_RESULT_MISMATCH");

  const resultRepro = scientificResult.reproducibility;
  if (!resultRepro || typeof resultRepro !== "object" || Array.isArray(resultRepro)) throw new Error("REPRO_CORE_MANIFEST_MISSING");
  const resultReproMap = resultRepro as Record<string, unknown>;
  if (String(resultReproMap.analysis_id ?? "") !== manifest.analysis_id || String(resultReproMap.execution_id ?? "") !== manifest.execution_id) {
    throw new Error("REPRO_IDENTIFIER_MISMATCH");
  }
  if (canonicalJsonText(resultReproMap) !== canonicalJsonText(manifest.scientific_core_manifest)) throw new Error("REPRO_CORE_MANIFEST_MISMATCH");
  const resultHashes = resultReproMap.hashes;
  if (!resultHashes || typeof resultHashes !== "object" || Array.isArray(resultHashes)) throw new Error("REPRO_CORE_HASHES_MISSING");
  if (String((resultHashes as Record<string, unknown>).raw_file_sha256 ?? "") !== manifest.hashes.engine_input_sha256) {
    throw new Error("REPRO_ENGINE_INPUT_CORE_HASH_MISMATCH");
  }
  return { files, manifest, specification, scientificResult };
}

export function verifyReproductionInputs(archiveBytes: Uint8Array, originalBytes: Uint8Array): VerifiedReproductionInputs {
  const verified = verifyReproducibilityArchive(archiveBytes);
  if (sha256HexSync(originalBytes) !== verified.manifest.hashes.raw_file_sha256) throw new Error("REPRO_ORIGINAL_FILE_SHA256_MISMATCH");
  let originalText: string;
  try {
    originalText = decoder.decode(originalBytes);
  } catch {
    throw new Error("REPRO_ORIGINAL_FILE_UTF8_INVALID");
  }
  const mappingRaw = verified.manifest.column_mapping;
  const mapping: ColumnMapping = {
    date: requireString(mappingRaw.date, "column_mapping.date"),
    securityReturn: requireString(mappingRaw.security_return, "column_mapping.security_return"),
    benchmarkReturn: requireString(mappingRaw.benchmark_return, "column_mapping.benchmark_return"),
  };
  const parsed = parseCsv(originalText);
  const sortApproved = verified.manifest.normalization.sorted_ascending_with_explicit_approval === true;
  const normalized = normalizeMappedCsv(parsed, mapping, sortApproved);
  const normalizationFile = parseJsonFile(verified.files, "normalization.json");
  const provenanceRaw = normalizationFile.normalized_to_original_source_row;
  if (!Array.isArray(provenanceRaw) || !provenanceRaw.every((value) => Number.isInteger(value))) throw new Error("REPRO_SOURCE_ROW_PROVENANCE_INVALID");
  const provenance = provenanceRaw.map(Number);
  if (!arraysEqual(normalized.normalizedToOriginalSourceRow, provenance)) throw new Error("REPRO_SOURCE_ROW_PROVENANCE_MISMATCH");
  if (normalized.sortedAscending !== sortApproved) throw new Error("REPRO_SORT_DECISION_MISMATCH");
  if (sha256HexSync(normalized.csvText) !== verified.manifest.hashes.engine_input_sha256) throw new Error("REPRO_ENGINE_INPUT_SHA256_MISMATCH");
  return {
    manifest: verified.manifest,
    specification: verified.specification,
    scientificResult: verified.scientificResult,
    normalizedCsvText: normalized.csvText,
    sourceRowProvenance: provenance,
  };
}

export function compareReproducedResult(verified: VerifiedReproductionInputs, reproducedResult: Record<string, unknown>): void {
  const repro = reproducedResult.reproducibility;
  if (!repro || typeof repro !== "object" || Array.isArray(repro)) throw new Error("REPRO_RERUN_MANIFEST_MISSING");
  const reproMap = repro as Record<string, unknown>;
  if (String(reproMap.analysis_id ?? "") !== verified.manifest.analysis_id) throw new Error("REPRO_RERUN_ANALYSIS_ID_MISMATCH");
  if (String(reproMap.execution_id ?? "") !== verified.manifest.execution_id) throw new Error("REPRO_RERUN_EXECUTION_ID_MISMATCH");
  const hashes = reproMap.hashes;
  if (!hashes || typeof hashes !== "object" || Array.isArray(hashes)) throw new Error("REPRO_RERUN_HASHES_MISSING");
  const hashMap = hashes as Record<string, unknown>;
  if (String(hashMap.raw_file_sha256 ?? "") !== verified.manifest.hashes.engine_input_sha256) throw new Error("REPRO_RERUN_ENGINE_INPUT_HASH_MISMATCH");
  if (String(hashMap.canonical_data_sha256 ?? "") !== verified.manifest.hashes.canonical_data_sha256) throw new Error("REPRO_RERUN_CANONICAL_HASH_MISMATCH");
  if (String(hashMap.specification_sha256 ?? "") !== verified.manifest.hashes.specification_sha256) throw new Error("REPRO_RERUN_SPECIFICATION_HASH_MISMATCH");
  const environment = reproMap.environment;
  if (!environment || typeof environment !== "object" || Array.isArray(environment)) throw new Error("REPRO_RERUN_ENVIRONMENT_MISSING");
  if (String((environment as Record<string, unknown>).build_commit ?? "") !== String(verified.manifest.build_provenance.build_commit ?? "")) {
    throw new Error("REPRO_RERUN_BUILD_COMMIT_MISMATCH");
  }
  if (sha256HexSync(canonicalJsonText(reproducedResult)) !== verified.manifest.scientific_result_sha256) {
    throw new Error("REPRO_RERUN_SCIENTIFIC_RESULT_MISMATCH");
  }
}
