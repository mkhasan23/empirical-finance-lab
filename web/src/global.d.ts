export {};
declare global {
  interface Window {
    __EFL_STAGE5__: {
      initialize(): Promise<Record<string, unknown>>;
      runFixture(fixtureId: string): Promise<{ result: Record<string, unknown>; mismatches: unknown[] }>;
      cancel(): void;
      getState(): string;
      getRuntime(): Record<string, unknown> | null;
      getLastResult(): Record<string, unknown> | null;
    };
    __EFL_STAGE6__: {
      getResult(): Record<string, unknown> | null;
      getLockedSpecification(): Record<string, unknown> | null;
      getRuntime(): Record<string, unknown> | null;
      getOriginalSha256(): string;
      getEngineInputSha256(): string;
    };
  }
}
