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
  }
}
