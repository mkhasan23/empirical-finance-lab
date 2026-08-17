import { EFLBrowserEngineClient, EFLBrowserError } from "./engineClient";
import { compareParity, scientificProjection } from "./parity";
import { transition, type AppState } from "./stateMachine";
import type { RuntimeManifest } from "./protocol";

type ParityCase = { fixture_id: string; raw_csv_text: string; specification: Record<string, unknown>; expected_outcome: Record<string, unknown> };
type ParityBundle = { schema_version: string; cases: ParityCase[] };

const status = document.querySelector<HTMLParagraphElement>("#status")!;
const output = document.querySelector<HTMLPreElement>("#output")!;
const initializeButton = document.querySelector<HTMLButtonElement>("#initialize")!;
const runButton = document.querySelector<HTMLButtonElement>("#run-ka003")!;
const cancelButton = document.querySelector<HTMLButtonElement>("#cancel")!;
let state: AppState = "EMPTY";
let client = new EFLBrowserEngineClient();
let runtime: RuntimeManifest | null = null;
let cases: ParityBundle | null = null;
let lastResult: Record<string, unknown> | null = null;

function setState(next: AppState, text: string) {
  state = transition(state, next);
  status.dataset.state = state;
  status.textContent = text;
}

async function loadCases(): Promise<ParityBundle> {
  if (cases) return cases;
  const response = await fetch(new URL("stage5-parity-cases.json", document.baseURI));
  if (!response.ok) throw new Error(`PARITY_CASES_FETCH_FAILED:${response.status}`);
  cases = await response.json() as ParityBundle;
  return cases;
}

async function initializeEngine(): Promise<RuntimeManifest> {
  if (state !== "EMPTY" && state !== "FAILED" && state !== "CANCELLED" && state !== "COMPLETE" && state !== "READY") throw new Error(`INIT_NOT_ALLOWED:${state}`);
  if (state === "READY" && runtime) return runtime;
  setState("ENGINE_LOADING", "Loading pinned Pyodide browser engine…");
  runtime = null;
  lastResult = null;
  runButton.disabled = true;
  output.textContent = "";
  try {
    runtime = await client.initialize(new URL("efl-core.json", document.baseURI).href);
    await loadCases();
    setState("READY", "Browser engine ready.");
    runButton.disabled = false;
    return runtime;
  } catch (error) {
    setState("FAILED", `Engine initialization failed: ${String(error)}`);
    throw error;
  }
}

async function runFixture(fixtureId: string): Promise<{ result: Record<string, unknown>; mismatches: ReturnType<typeof compareParity> }> {
  if (state !== "READY" && state !== "COMPLETE" && state !== "FAILED" && state !== "CANCELLED") throw new Error(`RUN_NOT_ALLOWED:${state}`);
  if (!runtime) await initializeEngine();
  const bundle = await loadCases();
  const fixture = bundle.cases.find((item) => item.fixture_id === fixtureId);
  if (!fixture) throw new Error(`PARITY_FIXTURE_NOT_FOUND:${fixtureId}`);
  if (state === "COMPLETE" || state === "FAILED" || state === "CANCELLED") state = "READY";
  setState("RUNNING", `Running ${fixtureId} inside Pyodide…`);
  cancelButton.disabled = false;
  lastResult = null;
  output.textContent = "";
  try {
    const result = await client.run(fixture.raw_csv_text, fixture.specification);
    const mismatches = compareParity(scientificProjection(result), scientificProjection(fixture.expected_outcome));
    lastResult = result;
    setState("COMPLETE", mismatches.length === 0 ? `${fixtureId}: parity PASS.` : `${fixtureId}: parity FAIL (${mismatches.length} mismatches).`);
    output.textContent = JSON.stringify({ fixture_id: fixtureId, mismatches, result }, null, 2);
    return { result, mismatches };
  } catch (error) {
    if (error instanceof EFLBrowserError && ["COMPUTATION_TIMEOUT", "WORKER_RUNTIME_ERROR", "WORKER_MESSAGE_ERROR", "ENGINE_NOT_READY"].includes(error.code)) {
      runtime = null;
      runButton.disabled = true;
    }
    if (!(error instanceof EFLBrowserError && error.code === "CANCELLED")) {
      setState("FAILED", `${fixtureId}: ${String(error)}`);
    }
    throw error;
  } finally {
    cancelButton.disabled = true;
  }
}

function cancelActive(): void {
  client.cancel();
  if (state === "RUNNING") setState("CANCELLED", "Active analysis cancelled; worker destroyed.");
  runtime = null;
  lastResult = null;
  runButton.disabled = true;
  cancelButton.disabled = true;
}

initializeButton.addEventListener("click", () => { void initializeEngine(); });
runButton.addEventListener("click", () => { void runFixture("KA-003"); });
cancelButton.addEventListener("click", cancelActive);

Object.assign(window, {
  __EFL_STAGE5__: {
    initialize: initializeEngine,
    runFixture,
    cancel: cancelActive,
    getState: () => state,
    getRuntime: () => runtime,
    getLastResult: () => lastResult,
  },
});
