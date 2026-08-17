import { EFLBrowserEngineClient, EFLBrowserError } from "./engineClient";
import { compareParity, scientificProjection } from "./parity";
import { transition, type AppState } from "./stateMachine";
import type { RuntimeManifest } from "./protocol";

type ParityCase = { fixture_id: string; raw_csv_text: string; specification: Record<string, unknown>; expected_outcome: Record<string, unknown> };
type ParityBundle = { schema_version: string; cases: ParityCase[] };

export function installStage5Harness(): void {
  let state: AppState = "EMPTY";
  const client = new EFLBrowserEngineClient();
  let runtime: RuntimeManifest | null = null;
  let cases: ParityBundle | null = null;
  let lastResult: Record<string, unknown> | null = null;

  async function loadCases(): Promise<ParityBundle> {
    if (cases) return cases;
    const response = await fetch(new URL("stage5-parity-cases.json", document.baseURI));
    if (!response.ok) throw new Error(`PARITY_CASES_FETCH_FAILED:${response.status}`);
    cases = await response.json() as ParityBundle;
    return cases;
  }

  async function initialize(): Promise<RuntimeManifest> {
    if (state === "READY" && runtime) return runtime;
    if (!["EMPTY", "FAILED", "CANCELLED", "COMPLETE", "READY"].includes(state)) throw new Error(`INIT_NOT_ALLOWED:${state}`);
    state = transition(state, "ENGINE_LOADING");
    runtime = null;
    lastResult = null;
    try {
      runtime = await client.initialize(new URL("efl-core.json", document.baseURI).href);
      await loadCases();
      state = transition(state, "READY");
      return runtime;
    } catch (error) {
      state = transition(state, "FAILED");
      throw error;
    }
  }

  async function runFixture(fixtureId: string): Promise<{ result: Record<string, unknown>; mismatches: ReturnType<typeof compareParity> }> {
    if (!["READY", "COMPLETE", "FAILED", "CANCELLED"].includes(state)) throw new Error(`RUN_NOT_ALLOWED:${state}`);
    if (!runtime) await initialize();
    const bundle = await loadCases();
    const fixture = bundle.cases.find((item) => item.fixture_id === fixtureId);
    if (!fixture) throw new Error(`PARITY_FIXTURE_NOT_FOUND:${fixtureId}`);
    if (["COMPLETE", "FAILED", "CANCELLED"].includes(state)) state = "READY";
    state = transition(state, "RUNNING");
    lastResult = null;
    try {
      const result = await client.run(fixture.raw_csv_text, fixture.specification);
      const mismatches = compareParity(scientificProjection(result), scientificProjection(fixture.expected_outcome));
      lastResult = result;
      state = transition(state, "COMPLETE");
      return { result, mismatches };
    } catch (error) {
      if (error instanceof EFLBrowserError && ["COMPUTATION_TIMEOUT", "WORKER_RUNTIME_ERROR", "WORKER_MESSAGE_ERROR", "ENGINE_NOT_READY"].includes(error.code)) runtime = null;
      if (!(error instanceof EFLBrowserError && error.code === "CANCELLED")) state = transition(state, "FAILED");
      throw error;
    }
  }

  function cancel(): void {
    client.cancel();
    if (state === "RUNNING") state = transition(state, "CANCELLED");
    runtime = null;
    lastResult = null;
  }

  Object.assign(window, {
    __EFL_STAGE5__: {
      initialize,
      runFixture,
      cancel,
      getState: () => state,
      getRuntime: () => runtime,
      getLastResult: () => lastResult,
    },
  });
}
