import { describe, expect, it } from "vitest";
import { defaultColumnMapping, normalizeMappedCsv, parseCsv, validateIntake } from "./csvIntake";

describe("Stage VI local CSV intake", () => {
  it("parses quoted fields and maps the canonical columns by default", () => {
    const parsed = parseCsv('date,security_return,benchmark_return,note\n2025-01-02,0.01,0.005,"a,b"\n');
    expect(parsed.headers).toEqual(["date", "security_return", "benchmark_return", "note"]);
    expect(parsed.rows[0]?.[3]).toBe("a,b");
    expect(defaultColumnMapping(parsed.headers)).toEqual({ date: "date", securityReturn: "security_return", benchmarkReturn: "benchmark_return" });
  });

  it("flags duplicate dates as CRITICAL before scientific execution", () => {
    const parsed = parseCsv("d,s,m\n2025-01-02,0.01,0.00\n2025-01-02,0.02,0.01\n");
    const report = validateIntake(parsed, { date: "d", securityReturn: "s", benchmarkReturn: "m" });
    expect(report.issues.some((issue) => issue.code === "DATA_DUPLICATE_DATE" && issue.severity === "CRITICAL")).toBe(true);
  });

  it("never sorts silently and preserves original source-row provenance after explicit sorting", () => {
    const parsed = parseCsv("d,s,m\n2025-01-03,0.02,0.01\n2025-01-02,0.01,0.00\n");
    const mapping = { date: "d", securityReturn: "s", benchmarkReturn: "m" };
    const report = validateIntake(parsed, mapping);
    expect(report.unsorted).toBe(true);
    expect(() => normalizeMappedCsv(parsed, mapping, false)).toThrow("SORT_APPROVAL_REQUIRED");
    const normalized = normalizeMappedCsv(parsed, mapping, true);
    expect(normalized.csvText).toBe("date,security_return,benchmark_return\n2025-01-02,0.01,0.00\n2025-01-03,0.02,0.01\n");
    expect(normalized.normalizedToOriginalSourceRow).toEqual([3, 2]);
  });
});
