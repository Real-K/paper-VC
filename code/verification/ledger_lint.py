# -*- coding: utf-8 -*-
"""CLAIMS_LEDGER 점검 — (1) 필수 열 (2) **claim_id 유일성** (3) 모든 행의 json_path 가 산출물에서 해석되고 값이 일치하는지
(4) 행의 sha256_16 가 산출물의 자기기록과 일치하는지(경고). P-014 에서 중복 claim_id 4건이 표는 맞게 그리면서 추적 사슬을
끊어놓은 사고가 있어 만든 검사. 설정: verify_config.json (ledger, artifacts_dir, extra_artifact_files). exit 1 = 중복 또는 불일치.
"""
import csv, json, os, sys
from collections import Counter
CFG_PATH = os.environ.get("VERIFY_CONFIG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8")); ROOT = os.path.dirname(os.path.abspath(CFG_PATH))
R = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))
rows = list(csv.DictReader(open(R(CFG["ledger"]), encoding="utf-8-sig")))
REQ = ["claim_id", "exhibit", "claim", "value", "ci95", "n", "source_json", "json_path", "code", "sha256_16", "path_status"]
missing_cols = [c for c in REQ if c not in rows[0]]; dups = [k for k, c in Counter(r["claim_id"] for r in rows).items() if c > 1]
def resolve(o, path):
    for k in [k for k in path.split(".") if k]: o = o[int(k)] if isinstance(o, list) else o[k]
    return o
extra = {os.path.basename(p): R(p) for p in CFG.get("extra_artifact_files", [])}
exact = derived = mismatch = nofile = shawarn = 0; bad = []
for r in rows:
    f = os.path.join(R(CFG["artifacts_dir"]), os.path.basename(r["source_json"]))
    if not os.path.exists(f): f = extra.get(os.path.basename(r["source_json"]), f)
    if not os.path.exists(f): nofile += 1; bad.append((r["claim_id"], "산출물 없음", os.path.basename(r["source_json"]))); continue
    d = json.load(open(f, encoding="utf-8"))
    if r["sha256_16"] and d.get("sha256_16") and r["sha256_16"] != d["sha256_16"]: shawarn += 1
    try: o = resolve(d, r["json_path"])
    except Exception: mismatch += 1; bad.append((r["claim_id"], "경로", r["json_path"][:60])); continue
    if isinstance(o, (dict, list)): derived += 1; continue
    try: ok = abs(float(r["value"]) - float(o)) <= max(5e-5, abs(float(o)) * 1e-6)
    except Exception: ok = str(o) == r["value"]
    if ok: exact += 1
    else: mismatch += 1; bad.append((r["claim_id"], "값", f"{r['value']} vs {o}"))
print(f"원장 {len(rows)}행 · 필수열 누락 {missing_cols or '없음'} · 중복 claim_id {dups or '없음'}")
print(f"해석: 정확 {exact} · 파생(객체) {derived} · 불일치 {mismatch} · 산출물 없음 {nofile} · sha 불일치(경고) {shawarn}")
for b in bad[:30]: print("  🔴", b)
print("상태 분포:", dict(Counter(r["path_status"] for r in rows)))
sys.exit(1 if (missing_cols or dups or mismatch or nofile) else 0)
