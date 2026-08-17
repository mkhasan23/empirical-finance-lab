import {
  ENGINE_INIT_TIMEOUT_MS,
  PUBLIC_PERMUTATION_CAP,
  PUBLIC_PERMUTATION_MIN,
  PUBLIC_ROW_CAP,
  PUBLIC_WATCHDOG_MS,
  WORKER_PROTOCOL_VERSION,
  type RuntimeManifest,
  type WorkerRequest,
  type WorkerResponse,
} from "./protocol";
import { acceptsResult } from "./stateMachine";

export class EFLBrowserError extends Error {
  constructor(public readonly code: string, message: string) { super(message); }
}

type WorkerLike = Pick<Worker, "postMessage" | "terminate" | "addEventListener" | "removeEventListener">;
type WorkerFactory = () => WorkerLike;
type PendingRequest = {
  kind: WorkerRequest["type"];
  worker: WorkerLike;
  timer: ReturnType<typeof setTimeout>;
  messageListener: EventListener;
  errorListener: EventListener;
  messageErrorListener: EventListener;
  reject: (reason: unknown) => void;
};

function makeId(prefix: string): string { return `${prefix}-${crypto.randomUUID()}`; }

function rowCount(rawCsvText: string): number {
  const lines = rawCsvText.split(/\r?\n/).filter((line) => line.trim().length > 0);
  return Math.max(0, lines.length - 1);
}

function permutationB(specification: Record<string, unknown>): number {
  const inference = specification.inference;
  if (!inference || typeof inference !== "object") return 20_000;
  const value = (inference as Record<string, unknown>).permutation_B;
  return typeof value === "number" ? value : 20_000;
}

export type EngineProgress = { phase: string; percent: number; operation: "INIT" | "RUN" };

export class EFLBrowserEngineClient {
  private worker: WorkerLike | null = null;
  private initialized = false;
  private activeJobId: string | null = null;
  private pending = new Map<string, PendingRequest>();
  private progressListener: ((progress: EngineProgress) => void) | null = null;

  constructor(
    private readonly workerFactory: WorkerFactory = () => new Worker(new URL("./eflWorker.ts", import.meta.url), { type: "module" }),
    private readonly watchdogMs = PUBLIC_WATCHDOG_MS,
    private readonly initTimeoutMs = ENGINE_INIT_TIMEOUT_MS,
  ) {}

  setProgressListener(listener: ((progress: EngineProgress) => void) | null): void {
    this.progressListener = listener;
  }

  private rejectPending(kind: WorkerRequest["type"], error: EFLBrowserError): void {
    for (const [requestId, pending] of this.pending) {
      if (pending.kind !== kind) continue;
      clearTimeout(pending.timer);
      pending.worker.removeEventListener("message", pending.messageListener);
      pending.worker.removeEventListener("error", pending.errorListener);
      pending.worker.removeEventListener("messageerror", pending.messageErrorListener);
      this.pending.delete(requestId);
      pending.reject(error);
    }
  }

  private terminateWorker(): void {
    this.worker?.terminate();
    this.worker = null;
    this.initialized = false;
    this.activeJobId = null;
  }

  private freshWorker(): WorkerLike {
    this.terminateWorker();
    this.worker = this.workerFactory();
    return this.worker;
  }

  private request<T extends WorkerResponse>(worker: WorkerLike, message: WorkerRequest, timeoutMs: number): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      let lastProgressPhase = message.type === "INIT" ? "awaiting_first_progress" : "running_analysis";
      const cleanup = () => {
        const pending = this.pending.get(message.requestId);
        if (!pending) return;
        clearTimeout(pending.timer);
        pending.worker.removeEventListener("message", pending.messageListener);
        pending.worker.removeEventListener("error", pending.errorListener);
        pending.worker.removeEventListener("messageerror", pending.messageErrorListener);
        this.pending.delete(message.requestId);
      };
      const armTimer = (): ReturnType<typeof setTimeout> => setTimeout(() => {
        cleanup();
        if (this.worker === worker) this.terminateWorker();
        const code = message.type === "INIT" ? "ENGINE_INIT_TIMEOUT" : "COMPUTATION_TIMEOUT";
        const qualifier = message.type === "INIT" ? ` after progress phase ${lastProgressPhase}` : "";
        reject(new EFLBrowserError(code, `Browser operation exceeded ${timeoutMs} ms${qualifier}.`));
      }, timeoutMs);
      const messageListener = ((event: MessageEvent<WorkerResponse>) => {
        const response = event.data;
        if (response.protocol !== WORKER_PROTOCOL_VERSION || response.requestId !== message.requestId) return;
        if (response.type === "PROGRESS") {
          lastProgressPhase = response.phase;
          this.progressListener?.({ phase: response.phase, percent: response.percent, operation: message.type });
          if (message.type === "INIT") {
            const pending = this.pending.get(message.requestId);
            if (pending) {
              clearTimeout(pending.timer);
              pending.timer = armTimer();
            }
          }
          return;
        }
        if (message.type === "RUN" && "jobId" in response && response.jobId && !acceptsResult(this.activeJobId, response.jobId)) {
          cleanup();
          reject(new EFLBrowserError("STALE_RESULT", "Discarded a stale or mismatched browser result."));
          return;
        }
        cleanup();
        if (response.type === "ERROR") reject(new EFLBrowserError(response.code, response.message));
        else resolve(response as T);
      }) as unknown as EventListener;
      const errorListener = ((event: Event) => {
        cleanup();
        if (this.worker === worker) this.terminateWorker();
        const eventMessage = (event as Event & { message?: unknown }).message;
        const messageText = typeof eventMessage === "string" && eventMessage ? eventMessage : "Browser worker failed before returning a structured response.";
        reject(new EFLBrowserError("WORKER_RUNTIME_ERROR", messageText));
      }) as EventListener;
      const messageErrorListener = (() => {
        cleanup();
        if (this.worker === worker) this.terminateWorker();
        reject(new EFLBrowserError("WORKER_MESSAGE_ERROR", "Browser worker message could not be deserialized."));
      }) as EventListener;
      const timer = armTimer();
      this.pending.set(message.requestId, { kind: message.type, worker, timer, messageListener, errorListener, messageErrorListener, reject });
      worker.addEventListener("message", messageListener);
      worker.addEventListener("error", errorListener);
      worker.addEventListener("messageerror", messageErrorListener);
      worker.postMessage(message);
    });
  }

  async initialize(coreBundleUrl: string): Promise<RuntimeManifest> {
    if (this.activeJobId !== null) throw new EFLBrowserError("ENGINE_BUSY", "Cannot reinitialize while an analysis is running.");
    if ([...this.pending.values()].some((pending) => pending.kind === "INIT")) throw new EFLBrowserError("ENGINE_INITIALIZING", "Browser engine initialization is already in progress.");
    const worker = this.freshWorker();
    const requestId = makeId("init");
    const response = await this.request<Extract<WorkerResponse, { type: "READY" }>>(worker, {
      protocol: WORKER_PROTOCOL_VERSION,
      type: "INIT",
      requestId,
      coreBundleUrl,
    }, this.initTimeoutMs);
    this.initialized = true;
    return response.runtime;
  }

  async run(rawCsvText: string, specification: Record<string, unknown>): Promise<Record<string, unknown>> {
    if (!this.worker || !this.initialized) throw new EFLBrowserError("ENGINE_NOT_READY", "Initialize the browser engine before analysis.");
    if (this.activeJobId !== null) throw new EFLBrowserError("ENGINE_BUSY", "Only one browser analysis may run at a time.");
    const rows = rowCount(rawCsvText);
    if (rows > PUBLIC_ROW_CAP) throw new EFLBrowserError("INPUT_ROW_LIMIT", `Input has ${rows} rows; v0.1 cap is ${PUBLIC_ROW_CAP}.`);
    const B = permutationB(specification);
    if (!Number.isInteger(B) || B < PUBLIC_PERMUTATION_MIN || B > PUBLIC_PERMUTATION_CAP) {
      throw new EFLBrowserError("PERMUTATION_B_LIMIT", `permutation_B must be an integer from ${PUBLIC_PERMUTATION_MIN} through ${PUBLIC_PERMUTATION_CAP}.`);
    }
    const requestId = makeId("run");
    const jobId = makeId("job");
    this.activeJobId = jobId;
    try {
      const response = await this.request<Extract<WorkerResponse, { type: "RESULT" }>>(this.worker, {
        protocol: WORKER_PROTOCOL_VERSION,
        type: "RUN",
        requestId,
        jobId,
        rawCsvText,
        specification,
      }, this.watchdogMs);
      if (!acceptsResult(this.activeJobId, response.jobId)) throw new EFLBrowserError("STALE_RESULT", "Discarded a stale browser result.");
      return response.result;
    } finally {
      if (this.activeJobId === jobId) this.activeJobId = null;
    }
  }

  cancel(): void {
    if (!this.worker || this.activeJobId === null) return;
    this.rejectPending("RUN", new EFLBrowserError("CANCELLED", "Analysis cancelled by user; worker destroyed."));
    this.terminateWorker();
  }

  dispose(): void {
    this.rejectPending("RUN", new EFLBrowserError("WORKER_DISPOSED", "Browser worker disposed."));
    this.rejectPending("INIT", new EFLBrowserError("WORKER_DISPOSED", "Browser worker disposed."));
    this.terminateWorker();
  }
}
