import { describe, expect, it } from "vitest";
import { buildReproducibilityFiles, crc32, createStoredZip, type BundleContext } from "./exportBundle";

const BUILD_COMMIT = "a".repeat(40);

function provenanceContext(runtimeCommit = BUILD_COMMIT): BundleContext {
  return {
    result: {
      state: "COMPLETE",
      specification: { model: "market_model" },
      audits: [],
      robustness: [],
      placebo: null,
      primary: { event_time: [], classical_inference: null, permutation_inference: null },
      reproducibility: {
        software_version: "0.0.0",
        analysis_id: "analysis-id",
        execution_id: "execution-id",
        hashes: {
          raw_file_sha256: "engine-input-hash",
          canonical_data_sha256: "canonical-hash",
          specification_sha256: "spec-hash",
        },
        environment: { build_commit: BUILD_COMMIT },
      },
    },
    originalUploadSha256: "original-hash",
    engineInputSha256: "engine-input-hash",
    columnMapping: { date: "date", security_return: "security", benchmark_return: "benchmark" },
    normalization: { sorted_ascending_with_explicit_approval: false, proprietary_raw_data_included: false },
    normalizedToOriginalSourceRow: [2, 3],
    runtime: {
      build_commit: runtimeCommit,
      build_mode: "github-pages",
      build_source: "github-actions",
      core_bundle_sha256: "b".repeat(64),
    },
  };
}

describe("Stage VI reproducibility ZIP", () => {
  it("uses the standard CRC-32 algorithm", () => {
    expect(crc32(new TextEncoder().encode("123456789"))).toBe(0xCBF43926);
  });

  it("creates deterministic stored ZIP bytes with local, central, and end records", () => {
    const first = createStoredZip({ "b.txt": "beta\n", "a.txt": "alpha\n" });
    const second = createStoredZip({ "a.txt": "alpha\n", "b.txt": "beta\n" });
    expect([...first]).toEqual([...second]);
    expect(Array.from(first.slice(0, 4))).toEqual([0x50, 0x4B, 0x03, 0x04]);
    const text = new TextDecoder().decode(first);
    expect(text).toContain("a.txt");
    expect(text).toContain("b.txt");
    expect(Array.from(first.slice(-22, -18))).toEqual([0x50, 0x4B, 0x05, 0x06]);
  });

  it("records one consistent build provenance authority across export metadata", () => {
    const files = buildReproducibilityFiles(provenanceContext());
    const manifest = JSON.parse(files["manifest.json"]!) as Record<string, unknown>;
    const environment = JSON.parse(files["environment.json"]!) as Record<string, unknown>;
    const expected = {
      build_commit: BUILD_COMMIT,
      build_mode: "github-pages",
      build_source: "github-actions",
      core_bundle_sha256: "b".repeat(64),
    };
    expect(manifest.build_provenance).toEqual(expected);
    expect(environment.build_provenance).toEqual(expected);
    expect(files["citation.txt"]).toContain(`Build commit: ${BUILD_COMMIT}.`);
    expect(files["README.txt"]).toContain(`Build commit: ${BUILD_COMMIT}`);
  });

  it("rejects disagreement between browser and scientific-core build commits", () => {
    expect(() => buildReproducibilityFiles(provenanceContext("c".repeat(40))))
      .toThrow("BUILD_PROVENANCE_COMMIT_MISMATCH");
  });
});
