import { describe, expect, it } from "vitest";
import { crc32, createStoredZip } from "./exportBundle";

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
});
