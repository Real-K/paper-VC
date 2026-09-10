# -*- coding: utf-8 -*-
"""청구→출처 앵커 검사. verify_draft 는 '어떤' 산출물에든 있으면 통과시키므로, 헤드라인 청구 각각을
**그 청구가 근거로 삼는 JSON 안에서** 확인한다(점추정은 맞고 CI 는 다른 산출물에서 온 조합을 잡는다).
설정: verify_config.json 의 anchors_file → {"anchors":[{"claim":"...","values":[...],"source":"X.json"}], "retired":{"claim":"사유"}}
"""
import json, os, sys
CFG_PATH = os.environ.get("VERIFY_CONFIG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8")); ROOT = os.path.dirname(os.path.abspath(CFG_PATH))
R = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))
A = json.load(open(R(CFG["anchors_file"]), encoding="utf-8")); OUT = R(CFG["artifacts_dir"]); TOL = float(A.get("tol", 5e-4))
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, (list, tuple)):
        for v in o: yield from walk(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool): yield float(o)
def has(vals, x): return any(abs(v - x) <= TOL or abs(v + x) <= TOL for v in vals)
bad, checked = [], 0
for a in A["anchors"]:
    p = os.path.join(OUT, a["source"])
    if not os.path.exists(p): bad.append((a["claim"], a["source"], "출처 없음", a["values"])); continue
    vals = list(walk(json.load(open(p, encoding="utf-8")))); miss = [x for x in a["values"] if not has(vals, x)]; checked += len(a["values"])
    if miss: bad.append((a["claim"], a["source"], "출처에 없음", miss))
retired = A.get("retired", {}); present = [c for c in retired if c in {a["claim"] for a in A["anchors"]}]
print(f"앵커 {len(A['anchors'])}청구 · 수치 {checked}개 대조")
for c, s, why, n in bad: print(f"  🔴 {c:<28} {s:<12} {why}: {n}")
if present:
    print(f"  ℹ️  폐기 앵커 {len(present)}건(산출물 보존·원고 비인용):"); [print(f"      {c} — {retired[c]}") for c in present]
print(f"\n총평: 불일치 {len(bad)}건"); sys.exit(1 if bad else 0)
