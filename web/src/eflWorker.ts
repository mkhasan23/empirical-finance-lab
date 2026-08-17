/// <reference lib="webworker" />
import {
  PYODIDE_INDEX_URL,
  PYODIDE_MODULE_URL,
  PYODIDE_VERSION,
  WORKER_PROTOCOL_VERSION,
  type WorkerRequest,
  type WorkerResponse,
} from "./protocol";

declare const self: DedicatedWorkerGlobalScope;

type PyodideApi = {
  FS: { mkdirTree(path: string): void; writeFile(path: string, data: Uint8Array | string, opts?: Record<string, unknown>): void };
  globals: { set(name: string, value: unknown): void; delete(name: string): boolean };
  loadPackage(
    packages: string[],
    options?: {
      messageCallback?: (message: string) => void;
      errorCallback?: (message: string) => void;
      checkIntegrity?: boolean;
    },
  ): Promise<unknown>;
  runPython(code: string): unknown;
};

type CoreBundle = {
  schema_version: string;
  bundle_sha256: string;
  files: Array<{ path: string; sha256: string; text: string }>;
};

let pyodide: PyodideApi | null = null;
let coreBundleSha256: string | null = null;

async function sha256Hex(text: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

function canonicalBundlePayload(bundle: CoreBundle): string {
  return bundle.files
    .map((file) => `${file.path}\n${file.sha256}`)
    .sort()
    .join("\n") + "\n";
}

async function installCore(bundleUrl: string, requestId: string): Promise<string> {
  send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "fetching_core_bundle", percent: 70 });
  const resolvedBundleUrl = new URL(bundleUrl, self.location.href);
  if (resolvedBundleUrl.origin !== self.location.origin) throw new Error("CORE_BUNDLE_ORIGIN_FORBIDDEN");
  const response = await fetch(resolvedBundleUrl.href, { cache: "no-store", credentials: "same-origin" });
  if (!response.ok) throw new Error(`CORE_BUNDLE_FETCH_FAILED:${response.status}`);
  const bundle = await response.json() as CoreBundle;
  send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "verifying_core_bundle", percent: 78 });
  if (bundle.schema_version !== "0.1.0") throw new Error("CORE_BUNDLE_SCHEMA_UNSUPPORTED");
  const bundleHash = await sha256Hex(canonicalBundlePayload(bundle));
  if (bundleHash !== bundle.bundle_sha256) throw new Error("CORE_BUNDLE_HASH_MISMATCH");
  if (!pyodide) throw new Error("PYODIDE_NOT_READY");
  send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "installing_core_bundle", percent: 86 });
  pyodide.FS.mkdirTree("/efl-core/empirical_finance_lab");
  for (const file of bundle.files) {
    const actual = await sha256Hex(file.text);
    if (actual !== file.sha256) throw new Error(`CORE_SOURCE_HASH_MISMATCH:${file.path}`);
    if (!file.path.startsWith("empirical_finance_lab/") || file.path.includes("..")) throw new Error("CORE_SOURCE_PATH_INVALID");
    pyodide.FS.writeFile(`/efl-core/${file.path}`, new TextEncoder().encode(file.text));
  }
  pyodide.runPython("import sys; sys.path.insert(0, '/efl-core') if '/efl-core' not in sys.path else None");
  send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "core_bundle_installed", percent: 92 });
  return bundleHash;
}

async function initialize(bundleUrl: string, requestId: string) {
  if (!pyodide) {
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "importing_pyodide_module", percent: 5 });
    const mod = await import(/* @vite-ignore */ PYODIDE_MODULE_URL) as { loadPyodide(options: { indexURL: string }): Promise<PyodideApi> };
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "initializing_python_runtime", percent: 15 });
    pyodide = await mod.loadPyodide({ indexURL: PYODIDE_INDEX_URL });
    const packageHeartbeat = (phase: string, percent: number) => ({
      messageCallback: (_message: string) => {
        send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase, percent });
      },
    });
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "loading_numpy", percent: 35 });
    await pyodide.loadPackage(["numpy"], packageHeartbeat("loading_numpy", 35));
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "loading_scipy", percent: 52 });
    await pyodide.loadPackage(["scipy"], packageHeartbeat("loading_scipy", 52));
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "scientific_runtime_loaded", percent: 65 });
  }
  coreBundleSha256 = await installCore(bundleUrl, requestId);
  send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId, phase: "importing_efl_core", percent: 96 });
  const runtimeJson = pyodide.runPython(`
import json, sys, numpy, scipy, empirical_finance_lab
json.dumps({
  "python_version": sys.version.split()[0],
  "numpy_version": numpy.__version__,
  "scipy_version": scipy.__version__,
  "efl_version": empirical_finance_lab.__version__,
}, separators=(",", ":"))
`) as string;
  const runtime = JSON.parse(runtimeJson) as { python_version: string; numpy_version: string; scipy_version: string; efl_version: string };
  return {
    protocol: WORKER_PROTOCOL_VERSION,
    pyodide_version: PYODIDE_VERSION,
    python_version: runtime.python_version,
    numpy_version: runtime.numpy_version,
    scipy_version: runtime.scipy_version,
    efl_version: runtime.efl_version,
    core_bundle_sha256: coreBundleSha256,
  };
}

async function runAnalysis(rawCsvText: string, specification: Record<string, unknown>): Promise<Record<string, unknown>> {
  if (!pyodide || !coreBundleSha256) throw new Error("ENGINE_NOT_READY");
  pyodide.globals.set("efl_raw_csv_text", rawCsvText);
  pyodide.globals.set("efl_spec_json", JSON.stringify(specification));
  try {
    const resultJson = pyodide.runPython(`
import json
from empirical_finance_lab import run_analysis, outcome_to_dict
_outcome = run_analysis(efl_raw_csv_text.encode("utf-8"), json.loads(efl_spec_json))
json.dumps(outcome_to_dict(_outcome), allow_nan=False, separators=(",", ":"), sort_keys=True)
`) as string;
    return JSON.parse(resultJson) as Record<string, unknown>;
  } finally {
    pyodide.globals.delete("efl_raw_csv_text");
    pyodide.globals.delete("efl_spec_json");
  }
}

function send(response: WorkerResponse) { self.postMessage(response); }

self.onmessage = async (event: MessageEvent<WorkerRequest>) => {
  const message = event.data;
  if (message.protocol !== WORKER_PROTOCOL_VERSION) {
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "ERROR", requestId: message.requestId, code: "WORKER_PROTOCOL_MISMATCH", message: "Unsupported worker protocol." });
    return;
  }
  try {
    if (message.type === "INIT") {
      send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId: message.requestId, phase: "loading_analysis_engine", percent: 10 });
      const runtime = await initialize(message.coreBundleUrl, message.requestId);
      send({ protocol: WORKER_PROTOCOL_VERSION, type: "READY", requestId: message.requestId, runtime });
      return;
    }
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "PROGRESS", requestId: message.requestId, jobId: message.jobId, phase: "running_analysis", percent: 20 });
    const result = await runAnalysis(message.rawCsvText, message.specification);
    send({ protocol: WORKER_PROTOCOL_VERSION, type: "RESULT", requestId: message.requestId, jobId: message.jobId, result });
  } catch (error) {
    const text = error instanceof Error ? error.message : String(error);
    if (message.type === "RUN") {
      send({ protocol: WORKER_PROTOCOL_VERSION, type: "ERROR", requestId: message.requestId, jobId: message.jobId, code: "BROWSER_ENGINE_ERROR", message: text });
    } else {
      send({ protocol: WORKER_PROTOCOL_VERSION, type: "ERROR", requestId: message.requestId, code: "BROWSER_ENGINE_ERROR", message: text });
    }
  }
};
