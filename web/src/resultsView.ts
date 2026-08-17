function asObject(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function asRows(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item)) : [];
}

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function formatPercent(value: unknown, digits = 3): string {
  const number = numberValue(value);
  return number === null ? "—" : `${(number * 100).toFixed(digits)}%`;
}

export function formatNumber(value: unknown, digits = 4): string {
  const number = numberValue(value);
  return number === null ? "—" : number.toFixed(digits);
}

export function formatPValue(value: unknown): string {
  const number = numberValue(value);
  if (number === null) return "—";
  if (number < 0.0001) return "<0.0001";
  return number.toFixed(4);
}

function clear(element: Element): void {
  while (element.firstChild) element.firstChild.remove();
}

function appendCell(row: HTMLTableRowElement, text: string, header = false): void {
  const cell = document.createElement(header ? "th" : "td");
  cell.textContent = text;
  if (header) cell.scope = "col";
  row.append(cell);
}

export function renderEventTable(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const primary = asObject(result.primary);
  const rows = asRows(primary.event_time);
  if (rows.length === 0) {
    container.textContent = "No event-time output is available.";
    return;
  }
  const table = document.createElement("table");
  table.className = "data-table";
  table.setAttribute("aria-label", "Event-time abnormal return results");
  const head = table.createTHead().insertRow();
  ["Date", "τ", "Security", "Benchmark", "Expected", "AR", "CAR"].forEach((label) => appendCell(head, label, true));
  const body = table.createTBody();
  for (const item of rows) {
    const row = body.insertRow();
    appendCell(row, String(item.date ?? ""));
    appendCell(row, String(item.tau ?? ""));
    appendCell(row, formatPercent(item.security_return));
    appendCell(row, formatPercent(item.benchmark_return));
    appendCell(row, formatPercent(item.expected_return));
    appendCell(row, formatPercent(item.abnormal_return));
    appendCell(row, formatPercent(item.cumulative_abnormal_return));
  }
  const wrapper = document.createElement("div");
  wrapper.className = "table-scroll";
  wrapper.append(table);
  container.append(wrapper);
}

function svgElement<K extends keyof SVGElementTagNameMap>(name: K, attrs: Record<string, string>): SVGElementTagNameMap[K] {
  const node = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

export function renderEventChart(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const primary = asObject(result.primary);
  const rows = asRows(primary.event_time);
  const points = rows.map((row) => ({ tau: Number(row.tau), ar: Number(row.abnormal_return), car: Number(row.cumulative_abnormal_return) }))
    .filter((row) => Number.isFinite(row.tau) && Number.isFinite(row.ar) && Number.isFinite(row.car));
  if (points.length === 0) {
    container.textContent = "No chart data available.";
    return;
  }
  const width = 720;
  const height = 300;
  const pad = 42;
  const values = points.flatMap((point) => [point.ar, point.car, 0]);
  const minY = Math.min(...values);
  const maxY = Math.max(...values);
  const span = maxY - minY || 1;
  const x = (index: number) => points.length === 1 ? width / 2 : pad + (index / (points.length - 1)) * (width - 2 * pad);
  const y = (value: number) => pad + ((maxY - value) / span) * (height - 2 * pad);

  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-labelledby": "event-chart-title event-chart-desc" });
  const title = svgElement("title", { id: "event-chart-title" });
  title.textContent = "Abnormal and cumulative abnormal returns across the event window";
  const desc = svgElement("desc", { id: "event-chart-desc" });
  desc.textContent = "Bars show abnormal returns by event time and the line shows cumulative abnormal returns. The event-time table provides exact values.";
  svg.append(title, desc);

  const zero = svgElement("line", { x1: String(pad), x2: String(width - pad), y1: String(y(0)), y2: String(y(0)), class: "chart-zero" });
  svg.append(zero);
  const barWidth = Math.min(44, (width - 2 * pad) / Math.max(points.length * 2, 1));
  points.forEach((point, index) => {
    const xCenter = x(index);
    const yValue = y(point.ar);
    const yZero = y(0);
    const rect = svgElement("rect", {
      x: String(xCenter - barWidth / 2),
      y: String(Math.min(yValue, yZero)),
      width: String(barWidth),
      height: String(Math.max(1, Math.abs(yZero - yValue))),
      class: "chart-bar",
    });
    const tauLabel = svgElement("text", { x: String(xCenter), y: String(height - 12), "text-anchor": "middle", class: "chart-label" });
    tauLabel.textContent = `τ=${point.tau}`;
    svg.append(rect, tauLabel);
  });
  const linePoints = points.map((point, index) => `${x(index)},${y(point.car)}`).join(" ");
  svg.append(svgElement("polyline", { points: linePoints, fill: "none", class: "chart-line" }));
  points.forEach((point, index) => svg.append(svgElement("circle", { cx: String(x(index)), cy: String(y(point.car)), r: "4", class: "chart-point" })));
  container.append(svg);
}

export function renderAuditList(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const audits = asRows(result.audits);
  if (audits.length === 0) {
    container.textContent = "No audit results are available.";
    return;
  }
  const order = ["CRITICAL", "WARNING", "NOT_ASSESSABLE", "PASS"];
  audits.sort((a, b) => order.indexOf(String(a.status)) - order.indexOf(String(b.status)));
  const list = document.createElement("ul");
  list.className = "audit-list";
  for (const audit of audits) {
    const item = document.createElement("li");
    const status = String(audit.status ?? "NOT_ASSESSABLE");
    item.className = `audit-item audit-${status.toLowerCase().replace("_", "-")}`;
    const badge = document.createElement("span");
    badge.className = "status-badge";
    badge.textContent = status.replace("_", " ");
    const content = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = `${String(audit.rule_id ?? "AUDIT")} · ${String(audit.stage ?? "")}`;
    const message = document.createElement("p");
    message.textContent = String(audit.message ?? "");
    content.append(title, message);
    item.append(badge, content);
    list.append(item);
  }
  container.append(list);
}

export function renderRobustness(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const rows = asRows(result.robustness);
  if (rows.length === 0) {
    container.textContent = "No robustness alternatives were prespecified for this run.";
    return;
  }
  const table = document.createElement("table");
  table.className = "data-table";
  table.setAttribute("aria-label", "Prespecified robustness matrix");
  const head = table.createTHead().insertRow();
  ["Model", "Window", "CAR", "Permutation p", "Sign", "5% conclusion"].forEach((label) => appendCell(head, label, true));
  const body = table.createTBody();
  for (const item of rows) {
    const row = body.insertRow();
    appendCell(row, String(item.model ?? ""));
    appendCell(row, Array.isArray(item.window) ? `[${item.window.join(", ")}]` : String(item.window ?? ""));
    appendCell(row, formatPercent(item.car));
    appendCell(row, formatPValue(item.permutation_p_value));
    appendCell(row, String(item.sign ?? ""));
    appendCell(row, item.significant_5pct === true ? "Significant" : "Not significant");
  }
  const wrapper = document.createElement("div");
  wrapper.className = "table-scroll";
  wrapper.append(table);
  container.append(wrapper);
}

export function renderPlacebo(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const placebo = asObject(result.placebo);
  if (Object.keys(placebo).length === 0) {
    container.textContent = "Historical placebo analysis was not enabled or was not available.";
    return;
  }
  const actual = numberValue(placebo.actual_car);
  const cars = Array.isArray(placebo.placebo_cars) ? placebo.placebo_cars.map(Number).filter(Number.isFinite) : [];
  const dates = Array.isArray(placebo.candidate_dates) ? placebo.candidate_dates.map(String) : [];
  const summary = document.createElement("p");
  summary.className = "metric-line";
  summary.textContent = `Actual CAR ${formatPercent(actual)} · ${String(placebo.candidate_count ?? cars.length)} admissible pseudo-events · historical tail proportion ${formatPValue(placebo.historical_placebo_tail_proportion)}.`;
  container.append(summary);
  if (cars.length === 0 || actual === null) return;

  const width = 720;
  const height = 260;
  const pad = 42;
  const values = [...cars, actual];
  const minY = Math.min(...values);
  const maxY = Math.max(...values);
  const span = maxY - minY || 1;
  const y = (value: number) => pad + ((maxY - value) / span) * (height - 2 * pad);
  const x = (index: number) => cars.length === 1 ? width / 2 : pad + (index / (cars.length - 1)) * (width - 2 * pad);
  const svg = svgElement("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-labelledby": "placebo-chart-title placebo-chart-desc" });
  const title = svgElement("title", { id: "placebo-chart-title" });
  title.textContent = "Historical placebo CAR distribution";
  const desc = svgElement("desc", { id: "placebo-chart-desc" });
  desc.textContent = "Dots show placebo-event CARs through historical candidate dates. The horizontal reference line marks the actual event CAR.";
  svg.append(title, desc);
  svg.append(svgElement("line", { x1: String(pad), x2: String(width - pad), y1: String(y(actual)), y2: String(y(actual)), class: "chart-actual" }));
  cars.forEach((car, index) => {
    const dot = svgElement("circle", { cx: String(x(index)), cy: String(y(car)), r: "3.25", class: "placebo-point" });
    const label = svgElement("title", {});
    label.textContent = `${dates[index] ?? `Candidate ${index + 1}`}: ${formatPercent(car)}`;
    dot.append(label);
    svg.append(dot);
  });
  container.append(svg);
}

export function renderReferee(container: HTMLElement, result: Record<string, unknown>): void {
  clear(container);
  const report = String(result.referee_report ?? "Referee Mode is not available.");
  const lines = report.split(/\r?\n/);
  for (const line of lines) {
    if (line.startsWith("# ")) {
      const heading = document.createElement("h3");
      heading.textContent = line.slice(2);
      container.append(heading);
    } else if (line.startsWith("**") && line.includes(":**") === false) {
      const paragraph = document.createElement("p");
      paragraph.textContent = line.replaceAll("**", "");
      paragraph.className = "referee-label";
      container.append(paragraph);
    } else if (line.trim() !== "") {
      const paragraph = document.createElement("p");
      paragraph.textContent = line.replaceAll("**", "");
      container.append(paragraph);
    }
  }
}

export function summaryMetrics(result: Record<string, unknown>): {
  state: string;
  car: string;
  permutationP: string;
  classicalP: string;
  model: string;
  window: string;
  analysisId: string;
} {
  const primary = asObject(result.primary);
  const permutation = asObject(primary.permutation_inference);
  const classical = asObject(primary.classical_inference);
  const spec = asObject(result.specification);
  const eventWindow = asObject(spec.event_window);
  const repro = asObject(result.reproducibility);
  return {
    state: String(result.state ?? "UNKNOWN"),
    car: formatPercent(primary.car),
    permutationP: formatPValue(permutation.p_value),
    classicalP: formatPValue(classical.p_value),
    model: String(spec.model ?? "—").replaceAll("_", " "),
    window: eventWindow.start === undefined ? "—" : `[${String(eventWindow.start)}, ${String(eventWindow.end)}]`,
    analysisId: String(repro.analysis_id ?? "—"),
  };
}
