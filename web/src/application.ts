import { EFLBrowserEngineClient, EFLBrowserError, type EngineProgress } from "./engineClient";
import {
  defaultColumnMapping,
  normalizeMappedCsv,
  parseCsv,
  sha256Hex,
  validateIntake,
  type ColumnMapping,
  type NormalizedCsv,
  type ParsedLocalCsv,
} from "./csvIntake";
import {
  DEFAULT_SPECIFICATION,
  buildLockedSpecification,
  cloneDraft,
  suggestEffectiveTradingDate,
  validateSpecificationDraft,
  type SpecificationDraft,
  type WindowDraft,
} from "./specification";
import { buildReproducibilityZip } from "./exportBundle";
import {
  renderAuditList,
  renderEventChart,
  renderEventTable,
  renderPlacebo,
  renderReferee,
  renderRobustness,
  summaryMetrics,
  formatNumber,
} from "./resultsView";
import type { RuntimeManifest } from "./protocol";

type PanelId = "intake" | "specification" | "lock" | "results";
type ResultTab = "summary" | "audits" | "robustness" | "placebo" | "referee" | "reproduce";

type Session = {
  file: File | null;
  originalBytes: Uint8Array | null;
  originalSha256: string;
  parsed: ParsedLocalCsv | null;
  mapping: ColumnMapping;
  normalized: NormalizedCsv | null;
  engineInputSha256: string;
  specDraft: SpecificationDraft;
  lockedSpec: Record<string, unknown> | null;
  result: Record<string, unknown> | null;
  runtime: RuntimeManifest | null;
};

const session: Session = {
  file: null,
  originalBytes: null,
  originalSha256: "",
  parsed: null,
  mapping: { date: "", securityReturn: "", benchmarkReturn: "" },
  normalized: null,
  engineInputSha256: "",
  specDraft: cloneDraft(DEFAULT_SPECIFICATION),
  lockedSpec: null,
  result: null,
  runtime: null,
};

const client = new EFLBrowserEngineClient();

function byId<T extends HTMLElement>(id: string): T {
  const node = document.getElementById(id);
  if (!node) throw new Error(`MISSING_UI_ELEMENT:${id}`);
  return node as T;
}

function input(id: string): HTMLInputElement { return byId<HTMLInputElement>(id); }
function select(id: string): HTMLSelectElement { return byId<HTMLSelectElement>(id); }
function button(id: string): HTMLButtonElement { return byId<HTMLButtonElement>(id); }

function setStatus(message: string, tone: "neutral" | "success" | "warning" | "critical" = "neutral"): void {
  const node = byId<HTMLElement>("app-status");
  node.textContent = message;
  node.dataset.tone = tone;
}

function showPanel(panel: PanelId): void {
  document.querySelectorAll<HTMLElement>("[data-workflow-panel]").forEach((node) => {
    node.hidden = node.dataset.workflowPanel !== panel;
  });
  document.querySelectorAll<HTMLButtonElement>("[data-step-target]").forEach((node) => {
    const active = node.dataset.stepTarget === panel;
    node.setAttribute("aria-current", active ? "step" : "false");
  });
  const target = byId<HTMLElement>(`panel-${panel}`);
  target.focus({ preventScroll: true });
  target.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
}

function clearDownstream(from: "file" | "mapping" | "spec"): void {
  if (from === "file" || from === "mapping") {
    session.normalized = null;
    session.engineInputSha256 = "";
  }
  session.lockedSpec = null;
  session.result = null;
  button("run-analysis").disabled = true;
  button("download-bundle").disabled = true;
  byId<HTMLElement>("result-shell").hidden = true;
  byId<HTMLElement>("lock-summary").textContent = "";
}

function populateMappingSelect(id: string, headers: string[], value: string): void {
  const control = select(id);
  control.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select a column…";
  control.append(placeholder);
  headers.forEach((header) => {
    const option = document.createElement("option");
    option.value = header;
    option.textContent = header || "(blank header)";
    control.append(option);
  });
  control.value = value;
  control.disabled = false;
}

function currentMapping(): ColumnMapping {
  return {
    date: select("map-date").value,
    securityReturn: select("map-security").value,
    benchmarkReturn: select("map-benchmark").value,
  };
}

function renderIntakeIssues(): void {
  const container = byId<HTMLElement>("intake-issues");
  container.replaceChildren();
  const continueButton = button("continue-to-specification");
  if (!session.parsed) {
    continueButton.disabled = true;
    return;
  }
  session.mapping = currentMapping();
  const report = validateIntake(session.parsed, session.mapping);
  const list = document.createElement("ul");
  list.className = "audit-list compact";
  for (const issue of report.issues) {
    const item = document.createElement("li");
    item.className = `audit-item audit-${issue.severity.toLowerCase()}`;
    const badge = document.createElement("span");
    badge.className = "status-badge";
    badge.textContent = issue.severity;
    const text = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = issue.code;
    const message = document.createElement("p");
    message.textContent = issue.sourceRows?.length ? `${issue.message} Rows: ${issue.sourceRows.slice(0, 10).join(", ")}${issue.sourceRows.length > 10 ? "…" : ""}` : issue.message;
    text.append(title, message);
    item.append(badge, text);
    list.append(item);
  }
  container.append(list);
  const sortWrap = byId<HTMLElement>("sort-approval-wrap");
  sortWrap.hidden = !report.unsorted;
  const blocked = report.issues.some((issue) => issue.severity === "CRITICAL") || (report.unsorted && !input("sort-approved").checked);
  continueButton.disabled = blocked;
  byId<HTMLElement>("intake-row-count").textContent = `${report.rowCount.toLocaleString()} rows`;
}

async function openLocalFile(file: File): Promise<void> {
  clearDownstream("file");
  session.file = file;
  const buffer = await file.arrayBuffer();
  session.originalBytes = new Uint8Array(buffer);
  session.originalSha256 = await sha256Hex(session.originalBytes);
  let parsed: ParsedLocalCsv;
  try {
    parsed = parseCsv(new TextDecoder("utf-8", { fatal: true }).decode(buffer));
  } catch (error) {
    session.parsed = null;
    setStatus(`Local file could not be parsed: ${String(error)}`, "critical");
    return;
  }
  session.parsed = parsed;
  session.mapping = defaultColumnMapping(parsed.headers);
  populateMappingSelect("map-date", parsed.headers, session.mapping.date);
  populateMappingSelect("map-security", parsed.headers, session.mapping.securityReturn);
  populateMappingSelect("map-benchmark", parsed.headers, session.mapping.benchmarkReturn);
  byId<HTMLElement>("file-name").textContent = file.name;
  byId<HTMLElement>("file-size").textContent = `${(file.size / 1024).toFixed(1)} KB`;
  byId<HTMLElement>("raw-hash").textContent = session.originalSha256;
  input("sort-approved").checked = false;
  renderIntakeIssues();
  setStatus("Local file opened in browser memory. No research data were transmitted.", "success");
}

function parseRobustnessWindows(): WindowDraft[] {
  const rows = [...document.querySelectorAll<HTMLElement>("[data-robustness-window]")];
  const windows: WindowDraft[] = [];
  for (const row of rows) {
    const startControl = row.querySelector<HTMLInputElement>("[data-window-start]");
    const endControl = row.querySelector<HTMLInputElement>("[data-window-end]");
    if (!startControl || !endControl) continue;
    if (startControl.value.trim() === "" && endControl.value.trim() === "") continue;
    windows.push({ start: Number(startControl.value), end: Number(endControl.value) });
  }
  return windows;
}

function syncDraftFromForm(): SpecificationDraft {
  const primaryModel = select("model").value as SpecificationDraft["model"];
  const alternativeModel = input("alternative-model").checked
    ? [primaryModel === "market_model" ? "market_adjusted" : "market_model"] as SpecificationDraft["robustnessModels"]
    : [];
  const excludedDates = (byId<HTMLTextAreaElement>("excluded-dates").value || "")
    .split(/[\s,]+/)
    .map((value) => value.trim())
    .filter(Boolean);
  session.specDraft = {
    returnUnits: select("return-units").value as SpecificationDraft["returnUnits"],
    model: primaryModel,
    calendarEventDate: input("calendar-event-date").value,
    effectiveEventDate: input("effective-event-date").value,
    eventTiming: select("event-timing").value as SpecificationDraft["eventTiming"],
    effectiveDateConfirmed: input("effective-date-confirmed").checked,
    estimationWindow: { start: Number(input("estimation-start").value), end: Number(input("estimation-end").value) },
    eventWindow: { start: Number(input("event-start").value), end: Number(input("event-end").value) },
    direction: select("direction").value as SpecificationDraft["direction"],
    directionalHypothesisPrespecified: input("one-sided-prespecified").checked,
    permutationB: Number(input("permutation-b").value),
    seed: Number(input("rng-seed").value),
    placeboEnabled: input("placebo-enabled").checked,
    excludedDates,
    robustnessModels: alternativeModel,
    robustnessWindows: parseRobustnessWindows(),
  };
  return session.specDraft;
}

function renderSpecIssues(): boolean {
  const draft = syncDraftFromForm();
  const issues = validateSpecificationDraft(draft);
  const container = byId<HTMLElement>("spec-issues");
  container.replaceChildren();
  if (issues.length === 0) {
    const ok = document.createElement("p");
    ok.className = "inline-success";
    ok.textContent = "Specification is internally ready to lock. The Python core remains authoritative for scientific validation.";
    container.append(ok);
  } else {
    const list = document.createElement("ul");
    list.className = "form-errors";
    issues.forEach((issue) => {
      const item = document.createElement("li");
      item.textContent = issue.message;
      list.append(item);
    });
    container.append(list);
  }
  button("review-lock").disabled = issues.length > 0;
  const oneSided = draft.direction !== "two_sided";
  byId<HTMLElement>("one-sided-ack-wrap").hidden = !oneSided;
  byId<HTMLElement>("model-alternative-label").textContent = draft.model === "market_model" ? "Also run market-adjusted model" : "Also run market model";
  return issues.length === 0;
}

function observedDates(): string[] {
  if (!session.parsed) return [];
  const mapping = currentMapping();
  const index = session.parsed.headers.indexOf(mapping.date);
  if (index < 0) return [];
  return session.parsed.rows.map((row) => (row[index] ?? "").trim()).filter(Boolean).sort();
}

function updateEventSuggestion(): void {
  const suggestion = suggestEffectiveTradingDate(
    input("calendar-event-date").value,
    select("event-timing").value as SpecificationDraft["eventTiming"],
    observedDates(),
  );
  const node = byId<HTMLElement>("event-date-suggestion");
  if (suggestion) {
    node.textContent = `Suggested effective trading date: ${suggestion}. You must confirm it explicitly.`;
    button("use-suggested-date").dataset.suggestedDate = suggestion;
    button("use-suggested-date").disabled = false;
  } else {
    node.textContent = "No effective trading date can be suggested from the mapped date series.";
    button("use-suggested-date").dataset.suggestedDate = "";
    button("use-suggested-date").disabled = true;
  }
  input("effective-date-confirmed").checked = false;
  renderSpecIssues();
}

function prepareSpecificationPanel(): void {
  const units = select("return-units").value as SpecificationDraft["returnUnits"];
  session.specDraft.returnUnits = units;
  input("calendar-event-date").value = session.specDraft.calendarEventDate;
  input("effective-event-date").value = session.specDraft.effectiveEventDate;
  select("event-timing").value = session.specDraft.eventTiming;
  input("estimation-start").value = String(session.specDraft.estimationWindow.start);
  input("estimation-end").value = String(session.specDraft.estimationWindow.end);
  input("event-start").value = String(session.specDraft.eventWindow.start);
  input("event-end").value = String(session.specDraft.eventWindow.end);
  select("model").value = session.specDraft.model;
  select("direction").value = session.specDraft.direction;
  input("permutation-b").value = String(session.specDraft.permutationB);
  input("rng-seed").value = String(session.specDraft.seed);
  input("placebo-enabled").checked = session.specDraft.placeboEnabled;
  input("alternative-model").checked = session.specDraft.robustnessModels.length > 0;
  input("effective-date-confirmed").checked = session.specDraft.effectiveDateConfirmed;
  renderSpecIssues();
}

async function finalizeIntakeAndContinue(): Promise<void> {
  if (!session.parsed || !session.originalBytes) return;
  session.mapping = currentMapping();
  const report = validateIntake(session.parsed, session.mapping);
  const sortApproved = input("sort-approved").checked;
  if (report.issues.some((issue) => issue.severity === "CRITICAL") || (report.unsorted && !sortApproved)) return;
  session.normalized = normalizeMappedCsv(session.parsed, session.mapping, sortApproved);
  session.engineInputSha256 = await sha256Hex(session.normalized.csvText);
  session.specDraft.returnUnits = select("return-units").value as SpecificationDraft["returnUnits"];
  prepareSpecificationPanel();
  setStatus("Input mapping is ready. Define the research specification before locking.", "neutral");
  showPanel("specification");
}

function renderLockSummary(spec: Record<string, unknown>): void {
  const container = byId<HTMLElement>("lock-summary");
  container.replaceChildren();
  const definition = document.createElement("dl");
  definition.className = "definition-grid";
  const add = (term: string, value: string) => {
    const dt = document.createElement("dt"); dt.textContent = term;
    const dd = document.createElement("dd"); dd.textContent = value;
    definition.append(dt, dd);
  };
  const est = spec.estimation_window as Record<string, unknown>;
  const evt = spec.event_window as Record<string, unknown>;
  const inf = spec.inference as Record<string, unknown>;
  add("Model", String(spec.model).replaceAll("_", " "));
  add("Calendar event", String(spec.calendar_event_date));
  add("Effective trading date", String(spec.effective_event_date));
  add("Estimation window", `[${String(est.start)}, ${String(est.end)}]`);
  add("Primary event window", `[${String(evt.start)}, ${String(evt.end)}]`);
  add("Inference", `${String(inf.direction).replaceAll("_", " ")}; B=${String(inf.permutation_B)}; seed=${String(inf.seed)}`);
  add("Placebo", (spec.placebo as Record<string, unknown>).enabled ? "Enabled" : "Disabled");
  add("Return units", String(spec.return_units));
  container.append(definition);
  const note = document.createElement("p");
  note.className = "lock-note";
  note.textContent = "Locking freezes these methodological choices for this run. Any later edit must start a new run; EFL will not search specifications for significance.";
  container.append(note);
}

function reviewAndLock(): void {
  if (!session.normalized || !renderSpecIssues()) return;
  const draft = syncDraftFromForm();
  const spec = buildLockedSpecification(draft, session.mapping, { sortedAscending: session.normalized.sortedAscending });
  session.lockedSpec = structuredClone(spec);
  renderLockSummary(session.lockedSpec);
  button("run-analysis").disabled = false;
  setStatus("Specification locked for this run. Numerical execution can now begin.", "success");
  showPanel("lock");
}

function renderModelDetails(result: Record<string, unknown>): void {
  const primary = result.primary && typeof result.primary === "object" ? result.primary as Record<string, unknown> : {};
  const model = primary.model && typeof primary.model === "object" ? primary.model as Record<string, unknown> : {};
  const container = byId<HTMLElement>("model-details");
  container.replaceChildren();
  const dl = document.createElement("dl");
  dl.className = "definition-grid compact-defs";
  const entries: Array<[string, string]> = [
    ["Usable estimation N", String(model.usable_estimation_n ?? "—")],
    ["α", formatNumber(model.alpha, 6)],
    ["β", formatNumber(model.beta, 6)],
    ["R²", formatNumber(model.r_squared, 4)],
    ["Residual scale", formatNumber(model.residual_scale, 6)],
  ];
  for (const [term, value] of entries) {
    const dt = document.createElement("dt"); dt.textContent = term;
    const dd = document.createElement("dd"); dd.textContent = value;
    dl.append(dt, dd);
  }
  container.append(dl);
}

function showResultTab(tab: ResultTab): void {
  document.querySelectorAll<HTMLElement>("[data-result-panel]").forEach((node) => { node.hidden = node.dataset.resultPanel !== tab; });
  document.querySelectorAll<HTMLButtonElement>("[data-result-tab]").forEach((node) => {
    const selected = node.dataset.resultTab === tab;
    node.setAttribute("aria-selected", selected ? "true" : "false");
    node.tabIndex = selected ? 0 : -1;
  });
}

function renderResult(result: Record<string, unknown>): void {
  const metrics = summaryMetrics(result);
  byId<HTMLElement>("metric-state").textContent = metrics.state;
  byId<HTMLElement>("metric-car").textContent = metrics.car;
  byId<HTMLElement>("metric-permutation").textContent = metrics.permutationP;
  byId<HTMLElement>("metric-classical").textContent = metrics.classicalP;
  byId<HTMLElement>("metric-model").textContent = metrics.model;
  byId<HTMLElement>("metric-window").textContent = metrics.window;
  byId<HTMLElement>("analysis-id").textContent = metrics.analysisId;
  renderModelDetails(result);
  renderEventChart(byId("event-chart"), result);
  renderEventTable(byId("event-table"), result);
  renderAuditList(byId("audit-results"), result);
  renderRobustness(byId("robustness-results"), result);
  renderPlacebo(byId("placebo-results"), result);
  renderReferee(byId("referee-results"), result);
  const repro = result.reproducibility && typeof result.reproducibility === "object" ? result.reproducibility as Record<string, unknown> : {};
  byId<HTMLElement>("execution-id").textContent = String(repro.execution_id ?? "—");
  byId<HTMLElement>("citation-version").textContent = String(repro.software_version ?? "0.0.0");
  byId<HTMLElement>("result-shell").hidden = false;
  button("download-bundle").disabled = result.state !== "COMPLETE";
  showResultTab("summary");
}

function progressText(progress: EngineProgress): string {
  return progress.phase.replaceAll("_", " ");
}

client.setProgressListener((progress) => {
  const bar = byId<HTMLProgressElement>("analysis-progress");
  bar.value = Math.max(0, Math.min(100, progress.percent));
  byId<HTMLElement>("analysis-progress-label").textContent = `${progress.operation === "INIT" ? "Engine" : "Analysis"}: ${progressText(progress)} (${Math.round(progress.percent)}%)`;
});

async function runLockedAnalysis(): Promise<void> {
  if (!session.lockedSpec || !session.normalized) return;
  const runButton = button("run-analysis");
  const cancelButton = button("cancel-analysis");
  runButton.disabled = true;
  cancelButton.disabled = false;
  byId<HTMLProgressElement>("analysis-progress").value = 0;
  byId<HTMLElement>("analysis-progress-wrap").hidden = false;
  setStatus("Initializing the pinned scientific runtime locally in your browser…", "neutral");
  showPanel("results");
  try {
    if (!session.runtime) {
      session.runtime = await client.initialize(new URL("efl-core.json", document.baseURI).href);
    }
    setStatus("Running the locked analysis in the validated Python core…", "neutral");
    const result = await client.run(session.normalized.csvText, session.lockedSpec);
    session.result = result;
    renderResult(result);
    if (result.state === "COMPLETE") setStatus("Analysis complete. Review the audit, robustness, placebo, and reproducibility outputs before interpreting the result.", "success");
    else setStatus("The scientific core blocked this analysis. Review CRITICAL and WARNING audit findings; no complete CAR is reported when the requested analysis is invalid.", "critical");
  } catch (error) {
    session.result = null;
    if (error instanceof EFLBrowserError && error.code === "CANCELLED") {
      setStatus("Analysis cancelled. The worker was destroyed; initialize a fresh run when ready.", "warning");
    } else {
      setStatus(`Analysis failed safely: ${error instanceof Error ? error.message : String(error)}`, "critical");
    }
    session.runtime = null;
  } finally {
    cancelButton.disabled = true;
    runButton.disabled = false;
    byId<HTMLElement>("analysis-progress-wrap").hidden = true;
  }
}

function cancelAnalysis(): void {
  client.cancel();
  session.runtime = null;
  setStatus("Cancellation requested. The active scientific worker was destroyed.", "warning");
}

function downloadBundle(): void {
  if (!session.result || !session.normalized) return;
  const { filename, bytes } = buildReproducibilityZip({
    result: session.result,
    originalUploadSha256: session.originalSha256,
    engineInputSha256: session.engineInputSha256,
    columnMapping: {
      date: session.mapping.date,
      security_return: session.mapping.securityReturn,
      benchmark_return: session.mapping.benchmarkReturn,
    },
    normalization: {
      sorted_ascending_with_explicit_approval: session.normalized.sortedAscending,
      proprietary_raw_data_included: false,
    },
    normalizedToOriginalSourceRow: session.normalized.normalizedToOriginalSourceRow,
    runtime: session.runtime as unknown as Record<string, unknown> | null,
  });
  const blob = new Blob([bytes], { type: "application/zip" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function newRunFromCurrent(): void {
  session.lockedSpec = null;
  session.result = null;
  button("download-bundle").disabled = true;
  button("run-analysis").disabled = true;
  byId<HTMLElement>("result-shell").hidden = true;
  setStatus("New draft created from the prior inputs. Any material edit will receive a new authoritative specification hash when executed.", "neutral");
  showPanel("specification");
}

function bindEvents(): void {
  input("file-input").addEventListener("change", (event) => {
    const file = (event.currentTarget as HTMLInputElement).files?.[0];
    if (file) void openLocalFile(file);
  });
  ["map-date", "map-security", "map-benchmark"].forEach((id) => select(id).addEventListener("change", () => { clearDownstream("mapping"); renderIntakeIssues(); }));
  input("sort-approved").addEventListener("change", renderIntakeIssues);
  select("return-units").addEventListener("change", () => { clearDownstream("mapping"); renderIntakeIssues(); });
  button("continue-to-specification").addEventListener("click", () => { void finalizeIntakeAndContinue(); });
  button("back-to-intake").addEventListener("click", () => showPanel("intake"));
  button("back-to-specification").addEventListener("click", () => showPanel("specification"));

  const specControls = [
    "calendar-event-date", "effective-event-date", "event-timing", "effective-date-confirmed",
    "estimation-start", "estimation-end", "event-start", "event-end", "model", "direction",
    "one-sided-prespecified", "permutation-b", "rng-seed", "placebo-enabled", "alternative-model", "excluded-dates",
    "robust-start-1", "robust-end-1", "robust-start-2", "robust-end-2", "robust-start-3", "robust-end-3",
  ];
  specControls.forEach((id) => byId<HTMLElement>(id).addEventListener("input", () => { clearDownstream("spec"); renderSpecIssues(); }));
  select("event-timing").addEventListener("change", updateEventSuggestion);
  input("calendar-event-date").addEventListener("change", updateEventSuggestion);
  button("use-suggested-date").addEventListener("click", () => {
    input("effective-event-date").value = button("use-suggested-date").dataset.suggestedDate ?? "";
    input("effective-date-confirmed").checked = false;
    renderSpecIssues();
  });
  button("review-lock").addEventListener("click", reviewAndLock);
  button("run-analysis").addEventListener("click", () => { void runLockedAnalysis(); });
  button("cancel-analysis").addEventListener("click", cancelAnalysis);
  button("download-bundle").addEventListener("click", downloadBundle);
  button("new-run").addEventListener("click", newRunFromCurrent);

  document.querySelectorAll<HTMLButtonElement>("[data-result-tab]").forEach((tab) => {
    tab.addEventListener("click", () => showResultTab(tab.dataset.resultTab as ResultTab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
      const tabs = [...document.querySelectorAll<HTMLButtonElement>("[data-result-tab]")];
      const index = tabs.indexOf(tab);
      const next = event.key === "ArrowRight" ? (index + 1) % tabs.length : (index - 1 + tabs.length) % tabs.length;
      tabs[next]!.focus();
      tabs[next]!.click();
    });
  });
}

export function initializeApplication(): void {
  bindEvents();
  showPanel("intake");
  showResultTab("summary");
  setStatus("Open a local CSV to begin. Research data remain in your browser session.", "neutral");
  Object.assign(window, {
    __EFL_STAGE6__: {
      getResult: () => session.result,
      getLockedSpecification: () => session.lockedSpec,
      getRuntime: () => session.runtime,
      getOriginalSha256: () => session.originalSha256,
      getEngineInputSha256: () => session.engineInputSha256,
    },
  });
}
