import { describe, expect, it } from "vitest";
import { acceptsResult, transition } from "./stateMachine";

describe("Stage V state machine", () => {
  it("permits the normal engine lifecycle", () => {
    expect(transition("EMPTY", "ENGINE_LOADING")).toBe("ENGINE_LOADING");
    expect(transition("ENGINE_LOADING", "READY")).toBe("READY");
    expect(transition("READY", "RUNNING")).toBe("RUNNING");
    expect(transition("RUNNING", "COMPLETE")).toBe("COMPLETE");
  });
  it("rejects stale results", () => {
    expect(acceptsResult("job-current", "job-current")).toBe(true);
    expect(acceptsResult("job-current", "job-old")).toBe(false);
    expect(acceptsResult(null, "job-old")).toBe(false);
  });
  it("rejects impossible transitions", () => {
    expect(() => transition("EMPTY", "COMPLETE")).toThrow(/INVALID_STATE_TRANSITION/);
  });
});
