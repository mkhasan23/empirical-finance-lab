declare const __EFL_BUILD_COMMIT__: string;
declare const __EFL_BUILD_MODE__: string;
declare const __EFL_BUILD_SOURCE__: string;

export type BuildProvenance = {
  build_commit: string;
  build_mode: string;
  build_source: string;
};

function validateBuildCommit(value: string): string {
  if (value === "UNSET" || /^[0-9a-f]{40}$/.test(value)) return value;
  throw new Error(`BUILD_COMMIT_INVALID:${value}`);
}

export const BUILD_PROVENANCE: Readonly<BuildProvenance> = Object.freeze({
  build_commit: validateBuildCommit(__EFL_BUILD_COMMIT__),
  build_mode: __EFL_BUILD_MODE__,
  build_source: __EFL_BUILD_SOURCE__,
});
