export type AppState = "EMPTY" | "ENGINE_LOADING" | "READY" | "RUNNING" | "COMPLETE" | "FAILED" | "CANCELLED";

const ALLOWED: Record<AppState, readonly AppState[]> = {
  EMPTY: ["ENGINE_LOADING"],
  ENGINE_LOADING: ["READY", "FAILED"],
  READY: ["RUNNING", "ENGINE_LOADING"],
  RUNNING: ["COMPLETE", "FAILED", "CANCELLED"],
  COMPLETE: ["RUNNING", "ENGINE_LOADING"],
  FAILED: ["ENGINE_LOADING", "RUNNING"],
  CANCELLED: ["ENGINE_LOADING", "RUNNING"],
};

export function transition(current: AppState, next: AppState): AppState {
  if (!ALLOWED[current].includes(next)) {
    throw new Error(`INVALID_STATE_TRANSITION:${current}->${next}`);
  }
  return next;
}

export function acceptsResult(activeJobId: string | null, incomingJobId: string): boolean {
  return activeJobId !== null && activeJobId === incomingJobId;
}
