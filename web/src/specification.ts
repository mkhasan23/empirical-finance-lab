import type { ColumnMapping } from "./csvIntake";

export type WindowDraft = { start: number; end: number };

export type SpecificationDraft = {
  returnUnits: "decimal" | "percent";
  model: "market_model" | "market_adjusted";
  calendarEventDate: string;
  effectiveEventDate: string;
  eventTiming: "during_or_before_market" | "after_market" | "uncertain";
  effectiveDateConfirmed: boolean;
  estimationWindow: WindowDraft;
  eventWindow: WindowDraft;
  direction: "two_sided" | "greater" | "less";
  directionalHypothesisPrespecified: boolean;
  permutationB: number;
  seed: number;
  placeboEnabled: boolean;
  excludedDates: string[];
  robustnessModels: Array<"market_model" | "market_adjusted">;
  robustnessWindows: WindowDraft[];
};

export type SpecIssue = { code: string; message: string };

export const DEFAULT_SPECIFICATION: SpecificationDraft = {
  returnUnits: "decimal",
  model: "market_model",
  calendarEventDate: "",
  effectiveEventDate: "",
  eventTiming: "uncertain",
  effectiveDateConfirmed: false,
  estimationWindow: { start: -250, end: -30 },
  eventWindow: { start: -1, end: 1 },
  direction: "two_sided",
  directionalHypothesisPrespecified: false,
  permutationB: 20_000,
  seed: 20_260_816,
  placeboEnabled: true,
  excludedDates: [],
  robustnessModels: ["market_adjusted"],
  robustnessWindows: [
    { start: 0, end: 0 },
    { start: -2, end: 2 },
  ],
};

function windowLength(window: WindowDraft): number {
  return window.end - window.start + 1;
}

export function validateSpecificationDraft(draft: SpecificationDraft): SpecIssue[] {
  const issues: SpecIssue[] = [];
  if (!draft.calendarEventDate) issues.push({ code: "EVENT_DATE_REQUIRED", message: "Enter the calendar announcement date." });
  if (!draft.effectiveEventDate || !draft.effectiveDateConfirmed) issues.push({ code: "EVENT_EFFECTIVE_CONFIRM_REQUIRED", message: "Confirm the effective event trading date explicitly." });
  if (draft.estimationWindow.start > draft.estimationWindow.end) issues.push({ code: "EST_WINDOW_INVALID", message: "Estimation-window start must not exceed its end." });
  if (draft.eventWindow.start > draft.eventWindow.end || windowLength(draft.eventWindow) > 11) issues.push({ code: "EVENT_WINDOW_INVALID", message: "Event window must be ordered and contain no more than 11 trading days." });
  if (draft.estimationWindow.start <= draft.eventWindow.end && draft.estimationWindow.end >= draft.eventWindow.start) issues.push({ code: "WINDOW_OVERLAP", message: "Estimation and event windows cannot overlap." });
  if (!Number.isInteger(draft.permutationB) || draft.permutationB < 1_000 || draft.permutationB > 100_000) issues.push({ code: "PERMUTATION_B_INVALID", message: "Permutation count must be an integer from 1,000 through 100,000." });
  if (!Number.isInteger(draft.seed) || draft.seed < 0) issues.push({ code: "SEED_INVALID", message: "Random seed must be a nonnegative integer." });
  if (draft.direction !== "two_sided" && !draft.directionalHypothesisPrespecified) issues.push({ code: "ONE_SIDED_ACK_REQUIRED", message: "A one-sided test requires explicit confirmation that the directional hypothesis was prespecified." });
  if (draft.robustnessWindows.length > 3) issues.push({ code: "ROBUSTNESS_WINDOW_LIMIT", message: "v0.1 permits at most three robustness windows." });
  for (const window of draft.robustnessWindows) {
    if (window.start > window.end || windowLength(window) > 11) issues.push({ code: "ROBUSTNESS_WINDOW_INVALID", message: "Every robustness window must be ordered and contain no more than 11 trading days." });
  }
  return issues;
}

export function suggestEffectiveTradingDate(calendarDate: string, eventTiming: SpecificationDraft["eventTiming"], observedDates: string[]): string {
  if (!calendarDate || observedDates.length === 0) return "";
  const sameDayIndex = observedDates.indexOf(calendarDate);
  if (sameDayIndex >= 0 && eventTiming !== "after_market") return calendarDate;
  const later = observedDates.find((date) => date > calendarDate);
  return later ?? "";
}

export function buildLockedSpecification(
  draft: SpecificationDraft,
  mapping: ColumnMapping,
  normalization: { sortedAscending: boolean },
): Record<string, unknown> {
  const issues = validateSpecificationDraft(draft);
  if (issues.length > 0) throw new Error(`SPECIFICATION_BLOCKED:${issues.map((issue) => issue.code).join(",")}`);
  const robustnessModels = draft.robustnessModels.filter((model) => model !== draft.model);
  return {
    schema_version: "0.1.0",
    return_units: draft.returnUnits,
    model: draft.model,
    calendar_event_date: draft.calendarEventDate,
    effective_event_date: draft.effectiveEventDate,
    event_timing: draft.eventTiming,
    estimation_window: { ...draft.estimationWindow },
    event_window: { ...draft.eventWindow },
    inference: {
      direction: draft.direction,
      permutation_B: draft.permutationB,
      seed: draft.seed,
    },
    locked: true,
    excluded_dates: [...draft.excludedDates],
    robustness_models: robustnessModels,
    robustness_windows: draft.robustnessWindows.map((window) => ({ ...window })),
    placebo: { enabled: draft.placeboEnabled },
    source_columns: {
      date: mapping.date,
      security_return: mapping.securityReturn,
      benchmark_return: mapping.benchmarkReturn,
    },
    normalization: {
      sorted_ascending_with_explicit_approval: normalization.sortedAscending,
    },
  };
}

export function cloneDraft(draft: SpecificationDraft): SpecificationDraft {
  return {
    ...draft,
    estimationWindow: { ...draft.estimationWindow },
    eventWindow: { ...draft.eventWindow },
    excludedDates: [...draft.excludedDates],
    robustnessModels: [...draft.robustnessModels],
    robustnessWindows: draft.robustnessWindows.map((window) => ({ ...window })),
  };
}
