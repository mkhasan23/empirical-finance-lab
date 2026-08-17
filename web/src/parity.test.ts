import { describe, expect, it } from "vitest";
import { compareParity, scientificProjection } from "./parity";

describe("cross-runtime parity comparator", () => {
  it("accepts continuous quantities inside Stage II tolerance", () => {
    expect(compareParity({ car: 0.03 + 1e-13 }, { car: 0.03 })).toHaveLength(0);
  });

  it("requires exact structural identity", () => {
    const mismatches = compareParity({ state: "COMPLETE" }, { state: "BLOCKED" });
    expect(mismatches).toHaveLength(1);
    expect(mismatches[0]?.reason).toBe("exact_mismatch");
  });

  it("excludes runtime-specific reproducibility identity from scientific parity", () => {
    const projected = scientificProjection({
      reproducibility: {
        analysis_id: "same",
        execution_id: "runtime-specific",
        environment: { python: "x" },
      },
    });
    expect(projected).toEqual({ reproducibility: { analysis_id: "same" } });
  });
});
