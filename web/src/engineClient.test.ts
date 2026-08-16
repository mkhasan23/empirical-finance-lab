import { describe, expect, it } from "vitest";
import { EFLBrowserEngineClient, EFLBrowserError } from "./engineClient";
import { WORKER_PROTOCOL_VERSION, type WorkerResponse } from "./protocol";

class FakeWorker {
  listeners = new Map<string, Set<EventListener>>();
  terminated = false;
  postMessage(message: any) {
    if (message.type === "INIT") queueMicrotask(() => this.emitMessage({
      protocol: WORKER_PROTOCOL_VERSION,
      type: "READY",
      requestId: message.requestId,
      runtime: { protocol: WORKER_PROTOCOL_VERSION, pyodide_version: "x", python_version: "x", numpy_version: "x", scipy_version: "x", efl_version: "x", core_bundle_sha256: "x" },
    }));
  }
  addEventListener(type: string, listener: EventListener) {
    const listeners = this.listeners.get(type) ?? new Set<EventListener>();
    listeners.add(listener);
    this.listeners.set(type, listeners);
  }
  removeEventListener(type: string, listener: EventListener) { this.listeners.get(type)?.delete(listener); }
  terminate() { this.terminated = true; }
  emitMessage(data: WorkerResponse) { for (const listener of this.listeners.get("message") ?? []) listener({ data } as unknown as Event); }
  emitError(message = "worker crash") { for (const listener of this.listeners.get("error") ?? []) listener({ message } as unknown as Event); }
}

describe("browser engine runtime controls", () => {
  it("enforces the 25,000-row cap before Python", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 1000);
    await client.initialize("/efl-core.json");
    const csv = "date,security_return,benchmark_return\n" + Array.from({ length: 25_001 }, (_, i) => `2025-01-${String((i % 28)+1).padStart(2,"0")},0,0`).join("\n");
    await expect(client.run(csv, { inference: { permutation_B: 1000 } })).rejects.toMatchObject({ code: "INPUT_ROW_LIMIT" });
  });


  it("enforces the Stage IV minimum permutation count before Python", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 1000);
    await client.initialize("/efl-core.json");
    await expect(client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 999 } })).rejects.toMatchObject({ code: "PERMUTATION_B_LIMIT" });
  });


  it("treats INIT timeout as a stall watchdog and refreshes it on progress", async () => {
    class ProgressingInitWorker extends FakeWorker {
      override postMessage(message: any) {
        if (message.type !== "INIT") return;
        setTimeout(() => this.emitMessage({
          protocol: WORKER_PROTOCOL_VERSION,
          type: "PROGRESS",
          requestId: message.requestId,
          phase: "initializing_python_runtime",
          percent: 25,
        }), 20);
        setTimeout(() => this.emitMessage({
          protocol: WORKER_PROTOCOL_VERSION,
          type: "PROGRESS",
          requestId: message.requestId,
          phase: "loading_scipy",
          percent: 60,
        }), 40);
        setTimeout(() => this.emitMessage({
          protocol: WORKER_PROTOCOL_VERSION,
          type: "READY",
          requestId: message.requestId,
          runtime: { protocol: WORKER_PROTOCOL_VERSION, pyodide_version: "x", python_version: "x", numpy_version: "x", scipy_version: "x", efl_version: "x", core_bundle_sha256: "x" },
        }), 55);
      }
    }
    const worker = new ProgressingInitWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 30);
    await expect(client.initialize("/efl-core.json")).resolves.toMatchObject({ protocol: WORKER_PROTOCOL_VERSION });
    expect(worker.terminated).toBe(false);
  });

  it("terminates a nonresponsive analysis on watchdog expiry", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 10, 1000);
    await client.initialize("/efl-core.json");
    await expect(client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 1000 } })).rejects.toMatchObject({ code: "COMPUTATION_TIMEOUT" });
    expect(worker.terminated).toBe(true);
  });

  it("rejects an active run immediately when cancelled", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 1000);
    await client.initialize("/efl-core.json");
    const promise = client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 1000 } });
    client.cancel();
    await expect(promise).rejects.toBeInstanceOf(EFLBrowserError);
    await expect(promise).rejects.toMatchObject({ code: "CANCELLED" });
    expect(worker.terminated).toBe(true);
  });

  it("rejects concurrent browser analyses rather than superseding an active job", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 1000);
    await client.initialize("/efl-core.json");
    const first = client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 1000 } });
    await expect(client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 1000 } })).rejects.toMatchObject({ code: "ENGINE_BUSY" });
    client.cancel();
    await expect(first).rejects.toMatchObject({ code: "CANCELLED" });
  });

  it("surfaces worker crashes immediately instead of waiting for the watchdog", async () => {
    const worker = new FakeWorker();
    const client = new EFLBrowserEngineClient(() => worker as unknown as Worker, 1000, 1000);
    await client.initialize("/efl-core.json");
    const promise = client.run("date,security_return,benchmark_return\n2025-01-01,0,0", { inference: { permutation_B: 1000 } });
    worker.emitError("boom");
    await expect(promise).rejects.toMatchObject({ code: "WORKER_RUNTIME_ERROR" });
    expect(worker.terminated).toBe(true);
  });
});
