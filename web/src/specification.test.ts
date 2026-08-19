import { describe, expect, it } from "vitest";
import { DEFAULT_SPECIFICATION, buildLockedSpecification, cloneDraft, suggestEffectiveTradingDate, validateSpecificationDraft } from "./specification";

describe("Stage VI specification locking", () => {
  it("requires explicit effective-date confirmation", () => {
    const draft = cloneDraft(DEFAULT_SPECIFICATION);
    draft.calendarEventDate = "2025-07-31";
    draft.effectiveEventDate = "2025-07-31";
    expect(validateSpecificationDraft(draft).some((issue) => issue.code === "EVENT_EFFECTIVE_CONFIRM_REQUIRED")).toBe(true);
    draft.effectiveDateConfirmed = true;
    expect(validateSpecificationDraft(draft)).toEqual([]);
  });

  it("requires a prespecification acknowledgement for one-sided inference", () => {
    const draft = cloneDraft(DEFAULT_SPECIFICATION);
    draft.calendarEventDate = "2025-07-31";
    draft.effectiveEventDate = "2025-07-31";
    draft.effectiveDateConfirmed = true;
    draft.direction = "greater";
    expect(validateSpecificationDraft(draft).some((issue) => issue.code === "ONE_SIDED_ACK_REQUIRED")).toBe(true);
    draft.directionalHypothesisPrespecified = true;
    expect(validateSpecificationDraft(draft)).toEqual([]);
  });

  it("suggests the next observed trading date for an after-market or non-trading-day event", () => {
    const dates = ["2025-07-31", "2025-08-01", "2025-08-04"];
    expect(suggestEffectiveTradingDate("2025-07-31", "during_or_before_market", dates)).toBe("2025-07-31");
    expect(suggestEffectiveTradingDate("2025-07-31", "after_market", dates)).toBe("2025-08-01");
    expect(suggestEffectiveTradingDate("2025-08-02", "uncertain", dates)).toBe("2025-08-04");
  });

  it("uses canonicalized YMD source dates for effective trading-date suggestions", () => {
    const slashDates = ["2024/05/22", "2024/05/23", "2024/05/24"];
    expect(suggestEffectiveTradingDate("2024-05-22", "after_market", slashDates)).toBe("2024-05-23");
    expect(suggestEffectiveTradingDate("2024-05-23", "during_or_before_market", slashDates)).toBe("2024-05-23");
    const compactDates = ["20240522", "20240523", "20240524"];
    expect(suggestEffectiveTradingDate("2024-05-23", "during_or_before_market", compactDates)).toBe("2024-05-23");
  });

  it("records mapping and explicit normalization inside the locked specification without changing the scientific core", () => {
    const draft = cloneDraft(DEFAULT_SPECIFICATION);
    draft.calendarEventDate = "2025-07-31";
    draft.effectiveEventDate = "2025-07-31";
    draft.effectiveDateConfirmed = true;
    const locked = buildLockedSpecification(draft, { date: "trade_date", securityReturn: "ret", benchmarkReturn: "mkt" }, { sortedAscending: true });
    expect(locked.locked).toBe(true);
    expect(locked.source_columns).toEqual({ date: "trade_date", security_return: "ret", benchmark_return: "mkt" });
    expect(locked.normalization).toEqual({ sorted_ascending_with_explicit_approval: true });
  });
});
