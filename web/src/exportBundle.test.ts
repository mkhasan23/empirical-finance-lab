import { describe, expect, it } from "vitest";
import { buildReproducibilityFiles, buildReproducibilityZip, crc32, createStoredZip, type BundleContext } from "./exportBundle";
import { compareReproducedResult, sha256HexSync, verifyReproductionInputs, verifyReproducibilityArchive } from "./reproRoundTrip";
import { readStoredZip } from "./storedZip";

const BUILD_COMMIT = "a".repeat(40);
const ORIGINAL_TEXT = "d,s,m\n2025-01-03,0.02,0.01\n2025-01-02,0.01,0.00\n";
const NORMALIZED_TEXT = "date,security_return,benchmark_return\n2025-01-02,0.01,0.00\n2025-01-03,0.02,0.01\n";
const ORIGINAL_HASH = sha256HexSync(ORIGINAL_TEXT);
const ENGINE_HASH = sha256HexSync(NORMALIZED_TEXT);

function provenanceContext(runtimeCommit = BUILD_COMMIT): BundleContext {
  return {
    result: {
      state: "COMPLETE",
      specification: {
        schema_version: "0.1.0",
        model: "market_model",
        source_columns: { date: "d", security_return: "s", benchmark_return: "m" },
        normalization: { sorted_ascending_with_explicit_approval: true },
      },
      audits: [],
      robustness: [],
      placebo: null,
      referee_report: "# Referee\n",
      primary: { car: 0.03, event_time: [], classical_inference: null, permutation_inference: null },
      reproducibility: {
        software_version: "0.0.0",
        analysis_id: "1".repeat(64),
        execution_id: "2".repeat(64),
        hashes: {
          raw_file_sha256: ENGINE_HASH,
          canonical_data_sha256: "3".repeat(64),
          specification_sha256: "4".repeat(64),
        },
        environment: { build_commit: BUILD_COMMIT },
        rng: { algorithm: "PCG64", seed: 1, permutation_B: 1000 },
        results: { car: 0.03 },
      },
    },
    originalUploadSha256: ORIGINAL_HASH,
    engineInputSha256: ENGINE_HASH,
    columnMapping: { date: "d", security_return: "s", benchmark_return: "m" },
    normalization: { sorted_ascending_with_explicit_approval: true, proprietary_raw_data_included: false },
    normalizedToOriginalSourceRow: [3, 2],
    runtime: {
      build_commit: runtimeCommit,
      build_mode: "github-pages",
      build_source: "github-actions",
      core_bundle_sha256: "b".repeat(64),
    },
  };
}

describe("Stage VII-D2 reproducibility round trip", () => {
  it("uses standard CRC-32 and SHA-256 algorithms", () => {
    expect(crc32(new TextEncoder().encode("123456789"))).toBe(0xCBF43926);
    expect(sha256HexSync("")).toBe("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    expect(sha256HexSync("abc")).toBe("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  });

  it("creates deterministic stored ZIP bytes and strictly reads them back", () => {
    const first = createStoredZip({ "b.txt": "beta\n", "a.txt": "alpha\n" });
    const second = createStoredZip({ "a.txt": "alpha\n", "b.txt": "beta\n" });
    expect([...first]).toEqual([...second]);
    expect(new TextDecoder().decode(readStoredZip(first)["a.txt"])).toBe("alpha\n");
    expect(Array.from(first.slice(0, 4))).toEqual([0x50, 0x4B, 0x03, 0x04]);
    expect(Array.from(first.slice(-22, -18))).toEqual([0x50, 0x4B, 0x05, 0x06]);
    expect(() => createStoredZip({ "../raw.csv": "forbidden\n" })).toThrow("ZIP_PATH_INVALID");

    const duplicate = first.slice();
    const needle = new TextEncoder().encode("b.txt");
    const replacement = new TextEncoder().encode("a.txt");
    for (let offset = 0; offset <= duplicate.length - needle.length; offset += 1) {
      if (needle.every((value, index) => duplicate[offset + index] === value)) duplicate.set(replacement, offset);
    }
    expect(() => readStoredZip(duplicate)).toThrow("ZIP_DUPLICATE_PATH");
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

  it("rejects disagreement between browser engine-input hash and the core raw-file hash", () => {
    const context = provenanceContext();
    context.engineInputSha256 = "f".repeat(64);
    expect(() => buildReproducibilityFiles(context)).toThrow("ENGINE_INPUT_HASH_MISMATCH");
  });

  it("self-validates the exact payload inventory and deterministic bundle-tree hash", () => {
    const first = buildReproducibilityZip(provenanceContext());
    const second = buildReproducibilityZip(provenanceContext());
    expect([...first.bytes]).toEqual([...second.bytes]);
    const verified = verifyReproducibilityArchive(first.bytes);
    expect(verified.manifest.bundle_schema).toBe("EFL_REPRODUCIBILITY_BUNDLE_V2");
    expect(verified.manifest.payload_integrity.algorithm).toBe("SHA-256");
    expect(verified.manifest.payload_integrity.files).toHaveLength(15);
    expect(verified.manifest.reproduction_contract.raw_research_data_included).toBe(false);
    expect(verified.files["scientific_result.json"]).toBeDefined();
  });

  it("reconstructs the exact normalized engine input from ZIP plus original local CSV", () => {
    const bundle = buildReproducibilityZip(provenanceContext());
    const verified = verifyReproductionInputs(bundle.bytes, new TextEncoder().encode(ORIGINAL_TEXT));
    expect(verified.normalizedCsvText).toBe(NORMALIZED_TEXT);
    expect(verified.sourceRowProvenance).toEqual([3, 2]);
    expect(verified.manifest.hashes.engine_input_sha256).toBe(ENGINE_HASH);
    expect(() => compareReproducedResult(verified, structuredClone(provenanceContext().result))).not.toThrow();
  });

  it("fails closed for the wrong original file, corrupted ZIP bytes, and altered manifest identity", () => {
    const bundle = buildReproducibilityZip(provenanceContext());
    expect(() => verifyReproductionInputs(bundle.bytes, new TextEncoder().encode(`${ORIGINAL_TEXT}x`)))
      .toThrow("REPRO_ORIGINAL_FILE_SHA256_MISMATCH");

    const corrupted = bundle.bytes.slice();
    corrupted[Math.floor(corrupted.length / 3)]! ^= 0x01;
    expect(() => verifyReproducibilityArchive(corrupted)).toThrow();

    const files = buildReproducibilityFiles(provenanceContext());
    const manifest = JSON.parse(files["manifest.json"]!) as Record<string, unknown>;
    manifest.analysis_id = "9".repeat(64);
    files["manifest.json"] = `${JSON.stringify(manifest, null, 2)}\n`;
    expect(() => verifyReproducibilityArchive(createStoredZip(files))).toThrow("REPRO_IDENTIFIER_MISMATCH");
  });

  it("detects any scientific-result drift after rerun", () => {
    const bundle = buildReproducibilityZip(provenanceContext());
    const verified = verifyReproductionInputs(bundle.bytes, new TextEncoder().encode(ORIGINAL_TEXT));
    const drifted = structuredClone(provenanceContext().result);
    (drifted.primary as Record<string, unknown>).car = 0.04;
    expect(() => compareReproducedResult(verified, drifted)).toThrow("REPRO_RERUN_SCIENTIFIC_RESULT_MISMATCH");
  });
});
