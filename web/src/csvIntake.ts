export type IntakeSeverity = "PASS" | "WARNING" | "CRITICAL";

export type IntakeIssue = {
  code: string;
  severity: IntakeSeverity;
  message: string;
  sourceRows?: number[];
};

export type ColumnMapping = {
  date: string;
  securityReturn: string;
  benchmarkReturn: string;
};

export type ParsedLocalCsv = {
  headers: string[];
  rows: string[][];
  rawText: string;
};

export type IntakeValidation = {
  issues: IntakeIssue[];
  rowCount: number;
  unsorted: boolean;
  duplicateDates: string[];
};

export type NormalizedCsv = {
  csvText: string;
  normalizedToOriginalSourceRow: number[];
  sortedAscending: boolean;
};

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

export function parseCsv(text: string): ParsedLocalCsv {
  const source = text.replace(/^\uFEFF/, "");
  const records: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;

  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i];
    if (quoted) {
      if (ch === '"') {
        if (source[i + 1] === '"') {
          field += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        field += ch;
      }
      continue;
    }

    if (ch === '"' && field.length === 0) {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && source[i + 1] === "\n") i += 1;
      row.push(field);
      records.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }

  if (quoted) throw new Error("CSV_UNCLOSED_QUOTE");
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    records.push(row);
  }

  while (records.length > 0 && records.at(-1)!.every((value) => value === "")) records.pop();
  if (records.length === 0) return { headers: [], rows: [], rawText: text };
  const headers = records[0]!;
  const rows = records.slice(1);
  return { headers, rows, rawText: text };
}

export function defaultColumnMapping(headers: string[]): ColumnMapping {
  return {
    date: headers.includes("date") ? "date" : "",
    securityReturn: headers.includes("security_return") ? "security_return" : "",
    benchmarkReturn: headers.includes("benchmark_return") ? "benchmark_return" : "",
  };
}

function validIsoDate(value: string): boolean {
  const match = ISO_DATE.exec(value.trim());
  if (!match) return false;
  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const d = new Date(Date.UTC(year, month - 1, day));
  return d.getUTCFullYear() === year && d.getUTCMonth() === month - 1 && d.getUTCDate() === day;
}

function columnIndex(headers: string[], name: string): number {
  return headers.indexOf(name);
}

export function validateIntake(parsed: ParsedLocalCsv, mapping: ColumnMapping): IntakeValidation {
  const issues: IntakeIssue[] = [];
  const rowCount = parsed.rows.length;
  const nonemptyHeaders = parsed.headers.filter((header) => header !== "");
  const duplicateHeaders = nonemptyHeaders.filter((header, index) => nonemptyHeaders.indexOf(header) !== index);
  if (parsed.headers.length === 0) {
    issues.push({ code: "INTAKE_NO_HEADER", severity: "CRITICAL", message: "The CSV has no header row." });
  }
  if (duplicateHeaders.length > 0) {
    issues.push({ code: "INTAKE_DUPLICATE_HEADER", severity: "CRITICAL", message: `Duplicate column names prevent unambiguous mapping: ${[...new Set(duplicateHeaders)].join(", ")}.` });
  }
  if (rowCount === 0) {
    issues.push({ code: "INTAKE_NO_ROWS", severity: "CRITICAL", message: "The CSV contains no data rows." });
  }
  if (rowCount > 25_000) {
    issues.push({ code: "DATA_TOO_MANY_ROWS", severity: "CRITICAL", message: `The file contains ${rowCount.toLocaleString()} rows; v0.1 accepts at most 25,000.` });
  }

  const selected = [mapping.date, mapping.securityReturn, mapping.benchmarkReturn];
  if (selected.some((value) => value === "")) {
    issues.push({ code: "INTAKE_MAPPING_REQUIRED", severity: "CRITICAL", message: "Map the date, security-return, and benchmark-return columns explicitly." });
    return { issues, rowCount, unsorted: false, duplicateDates: [] };
  }
  if (new Set(selected).size !== 3) {
    issues.push({ code: "INTAKE_MAPPING_COLLISION", severity: "CRITICAL", message: "Each required field must map to a different source column." });
    return { issues, rowCount, unsorted: false, duplicateDates: [] };
  }

  const dateIndex = columnIndex(parsed.headers, mapping.date);
  const secIndex = columnIndex(parsed.headers, mapping.securityReturn);
  const benchIndex = columnIndex(parsed.headers, mapping.benchmarkReturn);
  if ([dateIndex, secIndex, benchIndex].some((index) => index < 0)) {
    issues.push({ code: "INTAKE_MAPPING_UNKNOWN", severity: "CRITICAL", message: "One or more selected source columns do not exist in the CSV header." });
    return { issues, rowCount, unsorted: false, duplicateDates: [] };
  }

  const malformedDateRows: number[] = [];
  const dates: string[] = [];
  parsed.rows.forEach((record, index) => {
    const dateValue = (record[dateIndex] ?? "").trim();
    if (!validIsoDate(dateValue)) malformedDateRows.push(index + 2);
    dates.push(dateValue);
  });
  if (malformedDateRows.length > 0) {
    issues.push({ code: "DATA_INVALID_DATE", severity: "CRITICAL", message: "One or more mapped dates are not valid ISO dates (YYYY-MM-DD).", sourceRows: malformedDateRows });
  }

  const counts = new Map<string, number>();
  for (const dateValue of dates) counts.set(dateValue, (counts.get(dateValue) ?? 0) + 1);
  const duplicateDates = [...counts.entries()].filter(([dateValue, count]) => dateValue !== "" && count > 1).map(([dateValue]) => dateValue);
  if (duplicateDates.length > 0) {
    issues.push({ code: "DATA_DUPLICATE_DATE", severity: "CRITICAL", message: `Duplicate dates are not permitted: ${duplicateDates.slice(0, 6).join(", ")}${duplicateDates.length > 6 ? "…" : ""}.` });
  }

  let unsorted = false;
  if (malformedDateRows.length === 0 && duplicateDates.length === 0) {
    unsorted = dates.some((dateValue, index) => index > 0 && dates[index - 1]! >= dateValue);
    if (unsorted) {
      issues.push({ code: "DATA_UNSORTED", severity: "WARNING", message: "Dates are not strictly ascending. EFL will not sort silently; explicit approval is required before normalization." });
    }
  }

  if (!issues.some((issue) => issue.severity === "CRITICAL")) {
    issues.unshift({ code: "INTAKE_STRUCTURE_READY", severity: "PASS", message: `Local intake checks completed for ${rowCount.toLocaleString()} data rows. Authoritative scientific validation still occurs in the Python core.` });
  }
  return { issues, rowCount, unsorted, duplicateDates };
}

function csvEscape(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

export function normalizeMappedCsv(parsed: ParsedLocalCsv, mapping: ColumnMapping, sortApproved: boolean): NormalizedCsv {
  const validation = validateIntake(parsed, mapping);
  if (validation.issues.some((issue) => issue.severity === "CRITICAL")) throw new Error("INTAKE_BLOCKED");
  if (validation.unsorted && !sortApproved) throw new Error("SORT_APPROVAL_REQUIRED");

  const dateIndex = columnIndex(parsed.headers, mapping.date);
  const secIndex = columnIndex(parsed.headers, mapping.securityReturn);
  const benchIndex = columnIndex(parsed.headers, mapping.benchmarkReturn);
  const rows = parsed.rows.map((record, index) => ({
    date: (record[dateIndex] ?? "").trim(),
    securityReturn: (record[secIndex] ?? "").trim(),
    benchmarkReturn: (record[benchIndex] ?? "").trim(),
    originalSourceRow: index + 2,
  }));
  if (validation.unsorted && sortApproved) rows.sort((a, b) => a.date.localeCompare(b.date));

  const lines = ["date,security_return,benchmark_return"];
  for (const row of rows) {
    lines.push([row.date, row.securityReturn, row.benchmarkReturn].map(csvEscape).join(","));
  }
  return {
    csvText: `${lines.join("\n")}\n`,
    normalizedToOriginalSourceRow: rows.map((row) => row.originalSourceRow),
    sortedAscending: validation.unsorted && sortApproved,
  };
}

export async function sha256Hex(data: ArrayBuffer | Uint8Array | string): Promise<string> {
  let bytes: Uint8Array;
  if (typeof data === "string") bytes = new TextEncoder().encode(data);
  else if (data instanceof Uint8Array) bytes = data;
  else bytes = new Uint8Array(data);
  const view = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
  const digest = await crypto.subtle.digest("SHA-256", view);
  return [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, "0")).join("");
}
