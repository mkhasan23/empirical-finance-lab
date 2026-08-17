export type ParityMismatch = { path: string; expected: unknown; actual: unknown; reason: string };

const ABS_TOL = 1e-12;
const REL_TOL = 1e-10;
const P_TOL = 1e-10;

function numericClose(a: number, b: number, path: string): boolean {
  if (!Number.isFinite(a) || !Number.isFinite(b)) return Object.is(a, b);
  const tol = path.toLowerCase().includes("p_value") || path.toLowerCase().includes("tail_proportion")
    ? P_TOL
    : ABS_TOL + REL_TOL * Math.abs(b);
  return Math.abs(a - b) <= tol;
}

export function compareParity(actual: unknown, expected: unknown, path = "$", out: ParityMismatch[] = []): ParityMismatch[] {
  if (typeof actual === "number" && typeof expected === "number") {
    if (!numericClose(actual, expected, path)) out.push({ path, actual, expected, reason: "numeric_tolerance" });
    return out;
  }
  if (Array.isArray(actual) && Array.isArray(expected)) {
    if (actual.length !== expected.length) {
      out.push({ path, actual: actual.length, expected: expected.length, reason: "array_length" });
      return out;
    }
    actual.forEach((value, i) => compareParity(value, expected[i], `${path}[${i}]`, out));
    return out;
  }
  if (actual && expected && typeof actual === "object" && typeof expected === "object") {
    const a = actual as Record<string, unknown>;
    const e = expected as Record<string, unknown>;
    const keys = new Set([...Object.keys(a), ...Object.keys(e)]);
    for (const key of [...keys].sort()) {
      if (!(key in a) || !(key in e)) {
        out.push({ path: `${path}.${key}`, actual: a[key], expected: e[key], reason: "key_set" });
      } else {
        compareParity(a[key], e[key], `${path}.${key}`, out);
      }
    }
    return out;
  }
  if (!Object.is(actual, expected)) out.push({ path, actual, expected, reason: "exact_mismatch" });
  return out;
}

export function scientificProjection(value: Record<string, unknown>): Record<string, unknown> {
  const clone = structuredClone(value);
  const repro = clone.reproducibility;
  if (repro && typeof repro === "object") {
    const r = repro as Record<string, unknown>;
    delete r.execution_id;
    delete r.environment;
  }
  return clone;
}
