import { createStoredZip, crc32 } from "./storedZip";
import {
  buildPayloadIntegrity,
  canonicalJsonText,
  REPRO_BUNDLE_SCHEMA,
  sha256HexSync,
  verifyReproducibilityArchive,
} from "./reproRoundTrip";

export { createStoredZip, crc32 } from "./storedZip";

// storedZip.ts preserves the accepted deterministic ZIP timestamp: 1980-01-01.

export type BundleContext = {
  result: Record<string, unknown>;
  originalUploadSha256: string;
  engineInputSha256: string;
  columnMapping: Record<string, string>;
  normalization: Record<string, unknown>;
  normalizedToOriginalSourceRow: number[];
  runtime: Record<string, unknown> | null;
};

const VERSION_DOI_BY_RELEASE: Record<string, string> = {
  "0.1.1": "10.5281/zenodo.22018410",
};
const EFL_CONCEPT_DOI = "10.5281/zenodo.22018409";

type ExportBuildProvenance = {
  build_commit: string;
  build_mode: string;
  build_source: string;
  core_bundle_sha256: string;
};

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

function resolveBuildProvenance(coreRepro: Record<string, unknown>, runtimeValue: Record<string, unknown> | null): ExportBuildProvenance {
  const coreEnvironment = objectValue(coreRepro.environment);
  const browserRuntime = objectValue(runtimeValue);
  const coreCommit = String(coreEnvironment.build_commit ?? "UNSET");
  const browserCommit = String(browserRuntime.build_commit ?? "UNSET");
  if (coreCommit !== browserCommit) throw new Error(`BUILD_PROVENANCE_COMMIT_MISMATCH:${coreCommit}:${browserCommit}`);

  const buildMode = String(browserRuntime.build_mode ?? "UNAVAILABLE");
  const buildSource = String(browserRuntime.build_source ?? "UNAVAILABLE");
  if (buildMode === "github-pages" && !/^[0-9a-f]{40}$/.test(browserCommit)) {
    throw new Error("BUILD_PROVENANCE_PAGES_COMMIT_INVALID");
  }

  return {
    build_commit: browserCommit,
    build_mode: buildMode,
    build_source: buildSource,
    core_bundle_sha256: String(browserRuntime.core_bundle_sha256 ?? "UNAVAILABLE"),
  };
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
  const coreRawHash = String(coreHashes.raw_file_sha256 ?? "");
  if (coreRawHash !== context.engineInputSha256) {
    throw new Error(`ENGINE_INPUT_HASH_MISMATCH:${coreRawHash}:${context.engineInputSha256}`);
  }
  const canonicalHash = String(coreHashes.canonical_data_sha256 ?? "UNAVAILABLE");
  const specHash = String(coreHashes.specification_sha256 ?? "UNAVAILABLE");
  const buildProvenance = resolveBuildProvenance(coreRepro, context.runtime);

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
  const releaseVersion = String(coreRepro.software_version ?? "UNAVAILABLE");
  const releaseTag = releaseVersion === "UNAVAILABLE" ? "UNAVAILABLE" : `v${releaseVersion}`;
  const releaseUrl = releaseTag === "UNAVAILABLE"
    ? "UNAVAILABLE"
    : `https://github.com/mkhasan23/empirical-finance-lab/releases/tag/${releaseTag}`;
  const versionDoi = VERSION_DOI_BY_RELEASE[releaseVersion] ?? "UNAVAILABLE";
  const citation = [
    "Empirical Finance Lab: Audit-First Tools for Credible Empirical Finance Research.",
    "Author: Muhammad Kamrul Hasan.",
    `Software version: ${releaseVersion}.`,
    `Build commit: ${buildProvenance.build_commit}.`,
    `Build mode/source: ${buildProvenance.build_mode}/${buildProvenance.build_source}.`,
    "Repository: https://github.com/mkhasan23/empirical-finance-lab",
    `Formal release tag: ${releaseTag}.`,
    `Release page: ${releaseUrl}`,
    `Version DOI: ${versionDoi}.`,
    `Concept DOI (all versions): ${EFL_CONCEPT_DOI}.`,
    "No version-specific DOI is claimed unless an archival DOI is actually minted and recorded with the release.",
    "",
  ].join("\n");
  const readme = [
    "Empirical Finance Lab reproducibility bundle",
    "===========================================",
    "",
    "This archive was generated locally in the browser. It does not include the proprietary/raw research file.",
    "A full reproduction therefore requires this ZIP plus the exact original local CSV used for the run.",
    "manifest.json records the SHA-256 of the original local file and the transformed engine input separately.",
    "analysis_spec.json is the locked research specification sent to the validated Python core.",
    "normalization.json documents column mapping, date interpretation/canonicalization provenance when applicable, any explicitly approved sort, and normalized-to-original source-row provenance.",
    "scientific_result.json records the complete deterministic scientific result returned by the authoritative Python core.",
    "The D2 round-trip contract verifies the ZIP structure and payload hashes, the original-file hash, reconstructed engine input, locked specification, AnalysisID, ExecutionID, build provenance, and scientific-result identity before requiring a byte-identical deterministic re-export.",
    "event_time.csv reports the event-window values returned by the scientific core; no econometric quantity is recomputed by the exporter.",
    "Referee Mode is a deterministic synthesis of version-controlled audit rules and is not causal certification.",
    "",
    `Software version: ${releaseVersion}`,
    `AnalysisID: ${analysisId}`,
    `ExecutionID: ${executionId}`,
    `Build commit: ${buildProvenance.build_commit}`,
    `Build mode/source: ${buildProvenance.build_mode}/${buildProvenance.build_source}`,
    `Version DOI: ${versionDoi}`,
    `Concept DOI (all versions): ${EFL_CONCEPT_DOI}`,
    "",
  ].join("\n");

  const payloadFiles: Record<string, string> = {
    "README.txt": readme,
    "analysis_spec.json": json(result.specification ?? null),
    "audit_report.json": json(audits),
    "citation.txt": citation,
    "data_audit.json": json({ audits, source_row_provenance: context.normalizedToOriginalSourceRow }),
    "environment.json": json({ core_environment: coreRepro.environment ?? null, browser_runtime: context.runtime, build_provenance: buildProvenance }),
    "event_time.csv": csvFromRows(["date", "tau", "security_return", "benchmark_return", "expected_return", "abnormal_return", "cumulative_abnormal_return"], eventRows),
    "inference.json": json(inference),
    "model_results.json": json(primary),
    "normalization.json": json({ column_mapping: context.columnMapping, normalization: context.normalization, normalized_to_original_source_row: context.normalizedToOriginalSourceRow }),
    "placebo_events.csv": csvFromRows(["date", "placebo_car"], placeboEvents),
    "placebo_summary.json": json(placeboSummary),
    "referee_report.md": String(result.referee_report ?? "# Empirical Finance Lab — Referee Mode\n\nNot available.\n"),
    "robustness.csv": csvFromRows(["model", "window", "car", "permutation_p_value", "permutation_ge_count", "B", "sign", "significant_5pct"], robustness.map((row) => ({ ...row, window: Array.isArray(row.window) ? row.window.join(":") : row.window }))),
    "scientific_result.json": json(result),
  };
  const payloadIntegrity = buildPayloadIntegrity(payloadFiles);
  const manifest = {
    bundle_schema: REPRO_BUNDLE_SCHEMA,
    software_version: coreRepro.software_version ?? "UNAVAILABLE",
    analysis_id: analysisId,
    execution_id: executionId,
    build_provenance: buildProvenance,
    hashes: {
      raw_file_sha256: context.originalUploadSha256,
      engine_input_sha256: coreRawHash,
      canonical_data_sha256: canonicalHash,
      specification_sha256: specHash,
    },
    column_mapping: context.columnMapping,
    normalization: context.normalization,
    scientific_core_manifest: coreRepro,
    scientific_result_sha256: sha256HexSync(canonicalJsonText(result)),
    reproduction_contract: {
      original_local_file_required: true,
      raw_research_data_included: false,
      deterministic_reexport_required: true,
    },
    payload_integrity: {
      algorithm: "SHA-256",
      files: payloadIntegrity.files,
      tree_sha256: payloadIntegrity.tree_sha256,
    },
  };
  return { ...payloadFiles, "manifest.json": json(manifest) };
}

export function buildReproducibilityZip(context: BundleContext): { filename: string; bytes: Uint8Array } {
  const files = buildReproducibilityFiles(context);
  const repro = objectValue(context.result.reproducibility);
  const executionId = String(repro.execution_id ?? "unavailable").replace(/[^a-zA-Z0-9]/g, "").slice(0, 12) || "unavailable";
  const bytes = createStoredZip(files);
  verifyReproducibilityArchive(bytes); // fail closed before the browser can offer a download
  return { filename: `efl-run-${executionId}.zip`, bytes };
}
