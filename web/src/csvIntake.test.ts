import { describe, expect, it } from "vitest";
import { canonicalizeUnambiguousDate, defaultColumnMapping, normalizeMappedCsv, parseCsv, validateIntake } from "./csvIntake";

describe("Stage VI local CSV intake", () => {
  it("parses quoted fields and maps the canonical columns by default", () => {
    const parsed = parseCsv('date,security_return,benchmark_return,note\n2025-01-02,0.01,0.005,"a,b"\n');
    expect(parsed.headers).toEqual(["date", "security_return", "benchmark_return", "note"]);
    expect(parsed.rows[0]?.[3]).toBe("a,b");
    expect(defaultColumnMapping(parsed.headers)).toEqual({ date: "date", securityReturn: "security_return", benchmarkReturn: "benchmark_return" });
  });

  it("canonicalizes supported unambiguous YMD source dates without changing return strings", () => {
    const parsed = parseCsv("DlyCalDt,DlyRet,vwretd\n2024/05/22,-0.004571,-0.003777\n2024/05/23,0.093196,-0.008627\n2024/05/24,0.025723,0.007304\n");
    const mapping = { date: "DlyCalDt", securityReturn: "DlyRet", benchmarkReturn: "vwretd" };
    const report = validateIntake(parsed, mapping);
    expect(report.issues.some((issue) => issue.code === "DATA_INVALID_DATE")).toBe(false);
    expect(report.issues.some((issue) => issue.code === "DATA_DATE_CANONICALIZED" && issue.severity === "PASS")).toBe(true);
    expect(report.dateCanonicalization).toEqual({ sourceFormats: ["YYYY/MM/DD"], canonicalFormat: "YYYY-MM-DD", transformedRows: 3 });
    const normalized = normalizeMappedCsv(parsed, mapping, false);
    expect(normalized.csvText).toBe(
      "date,security_return,benchmark_return\n" +
      "2024-05-22,-0.004571,-0.003777\n" +
      "2024-05-23,0.093196,-0.008627\n" +
      "2024-05-24,0.025723,0.007304\n",
    );
    expect(normalized.normalizedToOriginalSourceRow).toEqual([2, 3, 4]);
  });

  it("accepts compact YYYYMMDD and rejects impossible calendar dates", () => {
    expect(canonicalizeUnambiguousDate("20240523")).toEqual({ canonical: "2024-05-23", sourceFormat: "YYYYMMDD" });
    expect(canonicalizeUnambiguousDate("2024/02/30")).toBeNull();
    expect(canonicalizeUnambiguousDate("05/06/2024")).toBeNull();
  });

  it("detects duplicates after date canonicalization", () => {
    const parsed = parseCsv("d,s,m\n2025-01-02,0.01,0.00\n2025/01/02,0.02,0.01\n");
    const report = validateIntake(parsed, { date: "d", securityReturn: "s", benchmarkReturn: "m" });
    expect(report.issues.some((issue) => issue.code === "DATA_DUPLICATE_DATE" && issue.severity === "CRITICAL")).toBe(true);
    expect(report.duplicateDates).toEqual(["2025-01-02"]);
  });

  it("warns on mixed but unambiguous YMD representations while preserving deterministic canonicalization", () => {
    const parsed = parseCsv("d,s,m\n2025-01-02,0.01,0.00\n2025/01/03,0.02,0.01\n20250104,0.03,0.02\n");
    const mapping = { date: "d", securityReturn: "s", benchmarkReturn: "m" };
    const report = validateIntake(parsed, mapping);
    expect(report.issues.some((issue) => issue.code === "DATA_DATE_FORMAT_MIXED" && issue.severity === "WARNING")).toBe(true);
    expect(normalizeMappedCsv(parsed, mapping, false).canonicalDates).toEqual(["2025-01-02", "2025-01-03", "2025-01-04"]);
  });

  it("never sorts silently and preserves original source-row provenance after canonicalization and explicit sorting", () => {
    const parsed = parseCsv("d,s,m\n2025/01/03,0.02,0.01\n2025/01/02,0.01,0.00\n");
    const mapping = { date: "d", securityReturn: "s", benchmarkReturn: "m" };
    const report = validateIntake(parsed, mapping);
    expect(report.unsorted).toBe(true);
    expect(() => normalizeMappedCsv(parsed, mapping, false)).toThrow("SORT_APPROVAL_REQUIRED");
    const normalized = normalizeMappedCsv(parsed, mapping, true);
    expect(normalized.csvText).toBe("date,security_return,benchmark_return\n2025-01-02,0.01,0.00\n2025-01-03,0.02,0.01\n");
    expect(normalized.normalizedToOriginalSourceRow).toEqual([3, 2]);
  });
});
