export const WORKER_PROTOCOL_VERSION = "0.1.0" as const;
export const PYODIDE_VERSION = "314.0.4" as const;
export const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/` as const;
export const PYODIDE_MODULE_URL = `${PYODIDE_INDEX_URL}pyodide.mjs` as const;
export const PUBLIC_ROW_CAP = 25_000;
export const PUBLIC_PERMUTATION_MIN = 1_000;
export const PUBLIC_PERMUTATION_CAP = 100_000;
export const PUBLIC_WATCHDOG_MS = 45_000;
// Initialization watchdog is inactivity-based: each valid INIT PROGRESS event refreshes it.
export const ENGINE_INIT_TIMEOUT_MS = 120_000;

export type WorkerRequest =
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "INIT"; requestId: string; coreBundleUrl: string }
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "RUN"; requestId: string; jobId: string; rawCsvText: string; specification: Record<string, unknown> };

export type RuntimeManifest = {
  protocol: string;
  pyodide_version: string;
  python_version: string;
  numpy_version: string;
  scipy_version: string;
  efl_version: string;
  core_bundle_sha256: string;
  build_commit: string;
  build_mode: string;
  build_source: string;
};

export type WorkerResponse =
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "READY"; requestId: string; runtime: RuntimeManifest }
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "PROGRESS"; requestId: string; jobId?: string; phase: string; percent: number }
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "RESULT"; requestId: string; jobId: string; result: Record<string, unknown> }
  | { protocol: typeof WORKER_PROTOCOL_VERSION; type: "ERROR"; requestId: string; jobId?: string; code: string; message: string; details?: Record<string, unknown> };
