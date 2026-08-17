const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8", { fatal: true });

export type StoredZipFiles = Record<string, Uint8Array>;

function u16(value: number): Uint8Array {
  const out = new Uint8Array(2);
  new DataView(out.buffer).setUint16(0, value, true);
  return out;
}

function u32(value: number): Uint8Array {
  const out = new Uint8Array(4);
  new DataView(out.buffer).setUint32(0, value >>> 0, true);
  return out;
}

function concat(parts: Uint8Array[]): Uint8Array {
  const total = parts.reduce((sum, part) => sum + part.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }
  return out;
}

function lexicalCompare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

function validatePath(name: string): void {
  if (
    name.length === 0 ||
    name.startsWith("/") ||
    name.endsWith("/") ||
    name.includes("\\") ||
    name.includes("\0") ||
    name.split("/").some((part) => part === "" || part === "." || part === "..")
  ) {
    throw new Error(`ZIP_PATH_INVALID:${name}`);
  }
}

let crcTable: Uint32Array | null = null;
function getCrcTable(): Uint32Array {
  if (crcTable) return crcTable;
  crcTable = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = (c & 1) !== 0 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    crcTable[n] = c >>> 0;
  }
  return crcTable;
}

export function crc32(bytes: Uint8Array): number {
  const table = getCrcTable();
  let crc = 0xFFFFFFFF;
  for (const byte of bytes) crc = table[(crc ^ byte) & 0xFF]! ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}

export function createStoredZip(files: Record<string, string>): Uint8Array {
  const entries = Object.entries(files)
    .sort(([a], [b]) => lexicalCompare(a, b))
    .map(([name, text]) => {
      validatePath(name);
      return { name, bytes: encoder.encode(text) };
    });
  if (entries.length === 0 || entries.length > 0xFFFF) throw new Error("ZIP_ENTRY_COUNT_INVALID");

  const localParts: Uint8Array[] = [];
  const centralParts: Uint8Array[] = [];
  let localOffset = 0;
  const utf8Flag = 0x0800;
  const dosTime = 0;
  const dosDate = 0x0021; // 1980-01-01, deterministic ZIP timestamp.

  for (const entry of entries) {
    const nameBytes = encoder.encode(entry.name);
    const crc = crc32(entry.bytes);
    const localHeader = concat([
      u32(0x04034B50), u16(20), u16(utf8Flag), u16(0), u16(dosTime), u16(dosDate),
      u32(crc), u32(entry.bytes.length), u32(entry.bytes.length), u16(nameBytes.length), u16(0), nameBytes,
    ]);
    localParts.push(localHeader, entry.bytes);

    const centralHeader = concat([
      u32(0x02014B50), u16(20), u16(20), u16(utf8Flag), u16(0), u16(dosTime), u16(dosDate),
      u32(crc), u32(entry.bytes.length), u32(entry.bytes.length), u16(nameBytes.length), u16(0), u16(0),
      u16(0), u16(0), u32(0), u32(localOffset), nameBytes,
    ]);
    centralParts.push(centralHeader);
    localOffset += localHeader.length + entry.bytes.length;
  }

  const central = concat(centralParts);
  const local = concat(localParts);
  const end = concat([
    u32(0x06054B50), u16(0), u16(0), u16(entries.length), u16(entries.length),
    u32(central.length), u32(local.length), u16(0),
  ]);
  return concat([local, central, end]);
}

function requireRange(bytes: Uint8Array, offset: number, length: number, label: string): void {
  if (!Number.isInteger(offset) || !Number.isInteger(length) || offset < 0 || length < 0 || offset + length > bytes.length) {
    throw new Error(`ZIP_RANGE_INVALID:${label}`);
  }
}

function readU16(bytes: Uint8Array, offset: number, label: string): number {
  requireRange(bytes, offset, 2, label);
  return new DataView(bytes.buffer, bytes.byteOffset + offset, 2).getUint16(0, true);
}

function readU32(bytes: Uint8Array, offset: number, label: string): number {
  requireRange(bytes, offset, 4, label);
  return new DataView(bytes.buffer, bytes.byteOffset + offset, 4).getUint32(0, true);
}

function decodeName(bytes: Uint8Array, offset: number, length: number): string {
  requireRange(bytes, offset, length, "name");
  let name: string;
  try {
    name = decoder.decode(bytes.subarray(offset, offset + length));
  } catch {
    throw new Error("ZIP_NAME_UTF8_INVALID");
  }
  validatePath(name);
  return name;
}

export function readStoredZip(bytes: Uint8Array): StoredZipFiles {
  if (bytes.length < 22) throw new Error("ZIP_TOO_SHORT");
  const eocdOffset = bytes.length - 22;
  if (readU32(bytes, eocdOffset, "eocd-signature") !== 0x06054B50) throw new Error("ZIP_EOCD_MISSING");
  if (readU16(bytes, eocdOffset + 4, "disk") !== 0 || readU16(bytes, eocdOffset + 6, "central-disk") !== 0) {
    throw new Error("ZIP_MULTIDISK_FORBIDDEN");
  }
  const entriesOnDisk = readU16(bytes, eocdOffset + 8, "entries-disk");
  const entryCount = readU16(bytes, eocdOffset + 10, "entries-total");
  if (entryCount === 0 || entriesOnDisk !== entryCount) throw new Error("ZIP_ENTRY_COUNT_INVALID");
  const centralSize = readU32(bytes, eocdOffset + 12, "central-size");
  const centralOffset = readU32(bytes, eocdOffset + 16, "central-offset");
  const commentLength = readU16(bytes, eocdOffset + 20, "comment-length");
  if (commentLength !== 0) throw new Error("ZIP_COMMENT_FORBIDDEN");
  if (centralOffset + centralSize !== eocdOffset) throw new Error("ZIP_CENTRAL_BOUNDARY_MISMATCH");

  const files: StoredZipFiles = {};
  const seen = new Set<string>();
  let centralPos = centralOffset;
  let expectedLocalOffset = 0;
  let priorName = "";

  for (let index = 0; index < entryCount; index += 1) {
    if (readU32(bytes, centralPos, "central-signature") !== 0x02014B50) throw new Error("ZIP_CENTRAL_HEADER_INVALID");
    const flags = readU16(bytes, centralPos + 8, "central-flags");
    const method = readU16(bytes, centralPos + 10, "central-method");
    const time = readU16(bytes, centralPos + 12, "central-time");
    const date = readU16(bytes, centralPos + 14, "central-date");
    const crc = readU32(bytes, centralPos + 16, "central-crc");
    const compressedSize = readU32(bytes, centralPos + 20, "central-compressed-size");
    const uncompressedSize = readU32(bytes, centralPos + 24, "central-uncompressed-size");
    const nameLength = readU16(bytes, centralPos + 28, "central-name-length");
    const extraLength = readU16(bytes, centralPos + 30, "central-extra-length");
    const commentLen = readU16(bytes, centralPos + 32, "central-comment-length");
    const diskStart = readU16(bytes, centralPos + 34, "central-disk-start");
    const localOffset = readU32(bytes, centralPos + 42, "local-offset");
    if (flags !== 0x0800 || method !== 0 || time !== 0 || date !== 0x0021) throw new Error("ZIP_FORMAT_UNSUPPORTED");
    if (compressedSize !== uncompressedSize) throw new Error("ZIP_STORED_SIZE_MISMATCH");
    if (extraLength !== 0 || commentLen !== 0 || diskStart !== 0) throw new Error("ZIP_METADATA_UNSUPPORTED");
    const name = decodeName(bytes, centralPos + 46, nameLength);
    if (seen.has(name)) throw new Error(`ZIP_DUPLICATE_PATH:${name}`);
    if (index > 0 && lexicalCompare(priorName, name) >= 0) throw new Error("ZIP_ENTRY_ORDER_INVALID");
    if (localOffset !== expectedLocalOffset) throw new Error("ZIP_LOCAL_OFFSET_NONCANONICAL");

    if (readU32(bytes, localOffset, "local-signature") !== 0x04034B50) throw new Error("ZIP_LOCAL_HEADER_INVALID");
    const localFlags = readU16(bytes, localOffset + 6, "local-flags");
    const localMethod = readU16(bytes, localOffset + 8, "local-method");
    const localTime = readU16(bytes, localOffset + 10, "local-time");
    const localDate = readU16(bytes, localOffset + 12, "local-date");
    const localCrc = readU32(bytes, localOffset + 14, "local-crc");
    const localCompressedSize = readU32(bytes, localOffset + 18, "local-compressed-size");
    const localUncompressedSize = readU32(bytes, localOffset + 22, "local-uncompressed-size");
    const localNameLength = readU16(bytes, localOffset + 26, "local-name-length");
    const localExtraLength = readU16(bytes, localOffset + 28, "local-extra-length");
    if (
      localFlags !== flags || localMethod !== method || localTime !== time || localDate !== date ||
      localCrc !== crc || localCompressedSize !== compressedSize || localUncompressedSize !== uncompressedSize ||
      localNameLength !== nameLength || localExtraLength !== 0
    ) {
      throw new Error("ZIP_LOCAL_CENTRAL_MISMATCH");
    }
    const localName = decodeName(bytes, localOffset + 30, localNameLength);
    if (localName !== name) throw new Error("ZIP_LOCAL_NAME_MISMATCH");
    const dataOffset = localOffset + 30 + localNameLength;
    requireRange(bytes, dataOffset, compressedSize, `data:${name}`);
    if (dataOffset + compressedSize > centralOffset) throw new Error("ZIP_DATA_OVERLAPS_CENTRAL_DIRECTORY");
    const data = bytes.slice(dataOffset, dataOffset + compressedSize);
    if (crc32(data) !== crc) throw new Error(`ZIP_CRC_MISMATCH:${name}`);

    files[name] = data;
    seen.add(name);
    priorName = name;
    expectedLocalOffset = dataOffset + compressedSize;
    centralPos += 46 + nameLength;
  }

  if (centralPos !== centralOffset + centralSize) throw new Error("ZIP_CENTRAL_SIZE_MISMATCH");
  if (expectedLocalOffset !== centralOffset) throw new Error("ZIP_LOCAL_REGION_MISMATCH");
  return files;
}
