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

export type DateInputMode = "auto" | "YYYY-MM-DD" | "YYYY/MM/DD" | "YYYYMMDD" | "MM/DD/YYYY" | "DD/MM/YYYY";
export type DateSourceFormat = Exclude<DateInputMode, "auto">;

export type DateCanonicalization = {
  requestedFormat: DateInputMode;
  sourceFormats: DateSourceFormat[];
  canonicalFormat: "YYYY-MM-DD";
  transformedRows: number;
  explicitAmbiguousFormatSelection: boolean;
};

export type IntakeValidation = {
  issues: IntakeIssue[];
  rowCount: number;
  unsorted: boolean;
  duplicateDates: string[];
  canonicalDates: string[];
  dateCanonicalization: DateCanonicalization;
};

export type NormalizedCsv = {
  csvText: string;
  normalizedToOriginalSourceRow: number[];
  sortedAscending: boolean;
  canonicalDates: string[];
  dateCanonicalization: DateCanonicalization;
};

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;
const YMD_SLASH_DATE = /^(\d{4})\/(\d{2})\/(\d{2})$/;
const YMD_COMPACT_DATE = /^(\d{4})(\d{2})(\d{2})$/;
const YEAR_LAST_SLASH_DATE = /^(\d{2})\/(\d{2})\/(\d{4})$/;

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

function preferredHeader(headers: string[], candidates: string[]): string {
  const byLower = new Map(headers.map((header) => [header.trim().toLowerCase(), header] as const));
  for (const candidate of candidates) {
    const match = byLower.get(candidate.toLowerCase());
    if (match !== undefined) return match;
  }
  return "";
}

export function defaultColumnMapping(headers: string[]): ColumnMapping {
  return {
    date: preferredHeader(headers, ["date", "DlyCalDt"]),
    securityReturn: preferredHeader(headers, ["security_return", "DlyRet"]),
    benchmarkReturn: preferredHeader(headers, ["benchmark_return", "vwretd"]),
  };
}

function validCalendarDate(year: number, month: number, day: number): boolean {
  const d = new Date(Date.UTC(year, month - 1, day));
  return d.getUTCFullYear() === year && d.getUTCMonth() === month - 1 && d.getUTCDate() === day;
}

function canonicalFromParts(year: number, month: number, day: number): string | null {
  if (!validCalendarDate(year, month, day)) return null;
  return `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function parseByMode(text: string, mode: DateSourceFormat): { canonical: string; sourceFormat: DateSourceFormat } | null {
  let match: RegExpExecArray | null;
  if (mode === "YYYY-MM-DD") {
    match = ISO_DATE.exec(text);
    if (!match) return null;
    const canonical = canonicalFromParts(Number(match[1]), Number(match[2]), Number(match[3]));
    return canonical ? { canonical, sourceFormat: mode } : null;
  }
  if (mode === "YYYY/MM/DD") {
    match = YMD_SLASH_DATE.exec(text);
    if (!match) return null;
    const canonical = canonicalFromParts(Number(match[1]), Number(match[2]), Number(match[3]));
    return canonical ? { canonical, sourceFormat: mode } : null;
  }
  if (mode === "YYYYMMDD") {
    match = YMD_COMPACT_DATE.exec(text);
    if (!match) return null;
    const canonical = canonicalFromParts(Number(match[1]), Number(match[2]), Number(match[3]));
    return canonical ? { canonical, sourceFormat: mode } : null;
  }
  match = YEAR_LAST_SLASH_DATE.exec(text);
  if (!match) return null;
  const first = Number(match[1]);
  const second = Number(match[2]);
  const year = Number(match[3]);
  const month = mode === "MM/DD/YYYY" ? first : second;
  const day = mode === "MM/DD/YYYY" ? second : first;
  const canonical = canonicalFromParts(year, month, day);
  return canonical ? { canonical, sourceFormat: mode } : null;
}

export function canonicalizeDate(value: string, mode: DateInputMode = "auto"): { canonical: string; sourceFormat: DateSourceFormat } | null {
  const text = value.trim();
  if (mode !== "auto") return parseByMode(text, mode);
  for (const candidate of ["YYYY-MM-DD", "YYYY/MM/DD", "YYYYMMDD"] as const) {
    const parsed = parseByMode(text, candidate);
    if (parsed) return parsed;
  }
  return null;
}

export function canonicalizeUnambiguousDate(value: string): { canonical: string; sourceFormat: DateSourceFormat } | null {
  return canonicalizeDate(value, "auto");
}

function columnIndex(headers: string[], name: string): number {
  return headers.indexOf(name);
}

function emptyDateCanonicalization(mode: DateInputMode): DateCanonicalization {
  return {
    requestedFormat: mode,
    sourceFormats: [],
    canonicalFormat: "YYYY-MM-DD",
    transformedRows: 0,
    explicitAmbiguousFormatSelection: mode === "MM/DD/YYYY" || mode === "DD/MM/YYYY",
  };
}

export function validateIntake(parsed: ParsedLocalCsv, mapping: ColumnMapping, dateInputMode: DateInputMode = "auto"): IntakeValidation {
  const issues: IntakeIssue[] = [];
  const rowCount = parsed.rows.length;
  const nonemptyHeaders = parsed.headers.filter((header) => header !== "");
  const duplicateHeaders = nonemptyHeaders.filter((header, index) => nonemptyHeaders.indexOf(header) !== index);
  const emptyResult = (extraIssues: IntakeIssue[]): IntakeValidation => ({
    issues: [...issues, ...extraIssues],
    rowCount,
    unsorted: false,
    duplicateDates: [],
    canonicalDates: [],
    dateCanonicalization: emptyDateCanonicalization(dateInputMode),
  });

  if (parsed.headers.length === 0) issues.push({ code: "INTAKE_NO_HEADER", severity: "CRITICAL", message: "The CSV has no header row." });
  if (duplicateHeaders.length > 0) issues.push({ code: "INTAKE_DUPLICATE_HEADER", severity: "CRITICAL", message: `Duplicate column names prevent unambiguous mapping: ${[...new Set(duplicateHeaders)].join(", ")}.` });
  if (rowCount === 0) issues.push({ code: "INTAKE_NO_ROWS", severity: "CRITICAL", message: "The CSV contains no data rows." });
  if (rowCount > 25_000) issues.push({ code: "DATA_TOO_MANY_ROWS", severity: "CRITICAL", message: `The file contains ${rowCount.toLocaleString()} rows; v0.1 accepts at most 25,000.` });

  const selected = [mapping.date, mapping.securityReturn, mapping.benchmarkReturn];
  if (selected.some((value) => value === "")) return emptyResult([{ code: "INTAKE_MAPPING_REQUIRED", severity: "CRITICAL", message: "Map the date, security-return, and benchmark-return columns explicitly." }]);
  if (new Set(selected).size !== 3) return emptyResult([{ code: "INTAKE_MAPPING_COLLISION", severity: "CRITICAL", message: "Each required field must map to a different source column." }]);

  const dateIndex = columnIndex(parsed.headers, mapping.date);
  const secIndex = columnIndex(parsed.headers, mapping.securityReturn);
  const benchIndex = columnIndex(parsed.headers, mapping.benchmarkReturn);
  if ([dateIndex, secIndex, benchIndex].some((index) => index < 0)) return emptyResult([{ code: "INTAKE_MAPPING_UNKNOWN", severity: "CRITICAL", message: "One or more selected source columns do not exist in the CSV header." }]);

  const malformedDateRows: number[] = [];
  const ambiguousDateRows: number[] = [];
  const canonicalDates: string[] = [];
  const sourceFormats = new Set<DateSourceFormat>();
  let transformedRows = 0;
  parsed.rows.forEach((record, index) => {
    const original = (record[dateIndex] ?? "").trim();
    const parsedDate = canonicalizeDate(original, dateInputMode);
    if (!parsedDate) {
      malformedDateRows.push(index + 2);
      if (dateInputMode === "auto" && YEAR_LAST_SLASH_DATE.test(original)) ambiguousDateRows.push(index + 2);
      canonicalDates.push(original);
      return;
    }
    canonicalDates.push(parsedDate.canonical);
    sourceFormats.add(parsedDate.sourceFormat);
    if (parsedDate.canonical !== original) transformedRows += 1;
  });

  const dateCanonicalization: DateCanonicalization = {
    requestedFormat: dateInputMode,
    sourceFormats: [...sourceFormats].sort(),
    canonicalFormat: "YYYY-MM-DD",
    transformedRows,
    explicitAmbiguousFormatSelection: dateInputMode === "MM/DD/YYYY" || dateInputMode === "DD/MM/YYYY",
  };

  if (ambiguousDateRows.length > 0) {
    issues.push({
      code: "DATA_AMBIGUOUS_DATE_FORMAT",
      severity: "CRITICAL",
      message: "Year-last slash dates are ambiguous under Auto. Explicitly choose MM/DD/YYYY or DD/MM/YYYY; EFL will never guess.",
      sourceRows: ambiguousDateRows,
    });
  }
  const nonAmbiguousMalformed = malformedDateRows.filter((row) => !ambiguousDateRows.includes(row));
  if (nonAmbiguousMalformed.length > 0) {
    issues.push({
      code: "DATA_INVALID_DATE",
      severity: "CRITICAL",
      message: `One or more mapped dates do not match the selected date format (${dateInputMode === "auto" ? "Auto: YYYY-MM-DD, YYYY/MM/DD, or YYYYMMDD" : dateInputMode}) or are impossible calendar dates.`,
      sourceRows: nonAmbiguousMalformed,
    });
  }
  if (dateCanonicalization.sourceFormats.length > 1 && malformedDateRows.length === 0) {
    issues.push({
      code: "DATA_DATE_FORMAT_MIXED",
      severity: "WARNING",
      message: `Multiple unambiguous date formats were detected (${dateCanonicalization.sourceFormats.join(", ")}); EFL will canonicalize them deterministically to YYYY-MM-DD without changing the original file.`,
    });
  }
  if (dateCanonicalization.explicitAmbiguousFormatSelection && malformedDateRows.length === 0) {
    issues.push({
      code: "DATA_DATE_FORMAT_EXPLICIT",
      severity: "PASS",
      message: `Explicit date interpretation ${dateInputMode} will be recorded in the locked preprocessing provenance.`,
    });
  }
  if (transformedRows > 0 && malformedDateRows.length === 0) {
    issues.push({
      code: "DATA_DATE_CANONICALIZED",
      severity: "PASS",
      message: `${transformedRows.toLocaleString()} mapped date value${transformedRows === 1 ? "" : "s"} will be canonicalized to YYYY-MM-DD for the scientific engine; original file bytes remain unchanged.`,
    });
  }

  const counts = new Map<string, number>();
  for (const dateValue of canonicalDates) counts.set(dateValue, (counts.get(dateValue) ?? 0) + 1);
  const duplicateDates = malformedDateRows.length === 0
    ? [...counts.entries()].filter(([dateValue, count]) => dateValue !== "" && count > 1).map(([dateValue]) => dateValue)
    : [];
  if (duplicateDates.length > 0) issues.push({ code: "DATA_DUPLICATE_DATE", severity: "CRITICAL", message: `Duplicate dates are not permitted after canonicalization: ${duplicateDates.slice(0, 6).join(", ")}${duplicateDates.length > 6 ? "…" : ""}.` });

  let unsorted = false;
  if (malformedDateRows.length === 0 && duplicateDates.length === 0) {
    unsorted = canonicalDates.some((dateValue, index) => index > 0 && canonicalDates[index - 1]! >= dateValue);
    if (unsorted) issues.push({ code: "DATA_UNSORTED", severity: "WARNING", message: "Dates are not strictly ascending after canonicalization. EFL will not sort silently; explicit approval is required before normalization." });
  }

  if (!issues.some((issue) => issue.severity === "CRITICAL")) issues.unshift({ code: "INTAKE_STRUCTURE_READY", severity: "PASS", message: `Local intake checks completed for ${rowCount.toLocaleString()} data rows. Authoritative scientific validation still occurs in the Python core.` });
  return { issues, rowCount, unsorted, duplicateDates, canonicalDates, dateCanonicalization };
}

function csvEscape(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}

export function normalizeMappedCsv(parsed: ParsedLocalCsv, mapping: ColumnMapping, sortApproved: boolean, dateInputMode: DateInputMode = "auto"): NormalizedCsv {
  const validation = validateIntake(parsed, mapping, dateInputMode);
  if (validation.issues.some((issue) => issue.severity === "CRITICAL")) throw new Error("INTAKE_BLOCKED");
  if (validation.unsorted && !sortApproved) throw new Error("SORT_APPROVAL_REQUIRED");

  const secIndex = columnIndex(parsed.headers, mapping.securityReturn);
  const benchIndex = columnIndex(parsed.headers, mapping.benchmarkReturn);
  const rows = parsed.rows.map((record, index) => ({
    date: validation.canonicalDates[index]!,
    securityReturn: (record[secIndex] ?? "").trim(),
    benchmarkReturn: (record[benchIndex] ?? "").trim(),
    originalSourceRow: index + 2,
  }));
  if (validation.unsorted && sortApproved) rows.sort((a, b) => a.date.localeCompare(b.date));

  const lines = ["date,security_return,benchmark_return"];
  for (const row of rows) lines.push([row.date, row.securityReturn, row.benchmarkReturn].map(csvEscape).join(","));
  return {
    csvText: `${lines.join("\n")}\n`,
    normalizedToOriginalSourceRow: rows.map((row) => row.originalSourceRow),
    sortedAscending: validation.unsorted && sortApproved,
    canonicalDates: rows.map((row) => row.date),
    dateCanonicalization: validation.dateCanonicalization,
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
