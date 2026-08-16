#!/usr/bin/env python3
"""Stage III repository/corpus integrity checker. No econometric calculations."""
from pathlib import Path
import csv, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'validation/manifest.json').read_text(encoding='utf-8'))
errors=[]
for item in manifest['fixtures']:
    for role,rel in item['files'].items():
        p=ROOT/rel
        if not p.exists():
            errors.append(f"{item['fixture_id']}: missing {role}: {rel}")
            continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        exp=item['sha256'][role]
        if h!=exp: errors.append(f"{item['fixture_id']}: SHA-256 mismatch for {rel}")
        if p.suffix=='.json':
            try: json.loads(p.read_text(encoding='utf-8'))
            except Exception as e: errors.append(f"{item['fixture_id']}: invalid JSON {rel}: {e}")
        if role=='data' and p.suffix=='.csv':
            with p.open(newline='',encoding='utf-8') as f:
                rows=list(csv.reader(f))
            if len(rows)<2: errors.append(f"{item['fixture_id']}: CSV has no data rows: {rel}")
required={'KA-001','KA-002','KA-003','KA-004','KA-005','INF-001','INF-002','PLC-001','ROB-001'}|{f'FM-{i:03d}' for i in range(1,16)}
seen={x['fixture_id'] for x in manifest['fixtures']}
if seen!=required:
    errors.append(f"fixture ID set mismatch; missing={sorted(required-seen)}, extra={sorted(seen-required)}")
for rel in ['README.md','LICENSE','CITATION.cff','pyproject.toml','docs/specifications/STAGE_I_SCIENTIFIC_SPEC.md','docs/specifications/STAGE_II_TECHNICAL_ARCHITECTURE.md','docs/specifications/STAGE_III_VALIDATION_CORPUS.md']:
    if not (ROOT/rel).exists(): errors.append(f"missing required repository file: {rel}")
if errors:
    print('STAGE III CORPUS INTEGRITY: FAIL')
    for e in errors: print(' -',e)
    sys.exit(1)
print(f"STAGE III CORPUS INTEGRITY: PASS ({manifest['fixture_count']} authoritative fixtures)")
