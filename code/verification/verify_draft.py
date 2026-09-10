# -*- coding: utf-8 -*-
"""원고 수치 검증 — 본문·부록·그림 캡션의 모든 수치가 원장 또는 집계 산출물에 존재하는지 대조한다.

설정: 같은 폴더의 verify_config.json 또는 $VERIFY_CONFIG. 경로는 설정 파일 위치 기준 상대경로.
설계 교훈(P-014/P-016): 전역 풀 방식은 **낡은 값이 풀 어딘가에 남아 있으면 통과**시킨다.
  → (a) 원장에 살아있는 행이 없는 산출물은 수확 제외(retired_artifacts)
  → (b) 원장 SUPERSEDED 행에서 차단 수치를 자동 도출(build_stale) + 수동 목록(manual_stale)
  → (c) 코드 안에만 있는 캡션 블록(caption_source 의 FIGCAP)도 대상에 포함
exit 1 = 미확인 수치 또는 폐기 수치 존재.
"""
import csv, re, os, sys, json, ast
from decimal import Decimal, ROUND_HALF_UP
CFG_PATH = os.environ.get("VERIFY_CONFIG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8")); ROOT = os.path.dirname(os.path.abspath(CFG_PATH))
R = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))
L = list(csv.DictReader(open(R(CFG["ledger"]), encoding="utf-8-sig")))
RETIRED = CFG.get("retired_artifacts", {}); MANUAL_STALE = {float(k): v for k, v in CFG.get("manual_stale", {}).items()}
POOL = {}
def add(v, src):
    try: x = float(v)
    except (TypeError, ValueError): return
    if not (abs(x) < 1e12): return
    for f in (1, 100, -1, -100):
        y = x * f
        for nd in range(0, 7):
            POOL.setdefault(round(y, nd), src)
            try: POOL.setdefault(float(Decimal(repr(y)).quantize(Decimal(1).scaleb(-nd), ROUND_HALF_UP)), src)
            except Exception: pass
def build_stale(rows):
    live, live_raw = set(), []
    for r in rows:
        if r["path_status"] == "SUPERSEDED": continue
        for t in [r["value"], r["n"]] + re.findall(r"-?\d+(?:\.\d+)?", r["ci95"] or ""):
            try: x = abs(float(t))
            except (TypeError, ValueError): continue
            live.add(round(x, 6)); live_raw.append(x)
    def collides(v, nd): return any(round(x, nd) == v for x in live_raw)
    def distinctive(t):
        try: x = abs(float(t))
        except (TypeError, ValueError): return None
        st = str(t).strip().lstrip("-"); frac = len(st.split(".")[1]) if "." in st else 0
        if not (frac >= 3 or (frac == 0 and x >= 1000)): return None
        return round(x, 6), frac
    out = {}
    for r in rows:
        if r["path_status"] != "SUPERSEDED": continue
        why = f"원장 {r['claim_id']} 폐기 — {r['claim'][:70]}"
        for t in [r["value"]] + re.findall(r"-?\d+(?:\.\d+)?", r["ci95"] or ""):
            d = distinctive(t)
            if d is None: continue
            v, nd = d
            if v in live or collides(v, nd): continue
            out.setdefault(v, why)
    return out
LIVE = [r for r in L if r["path_status"] != "SUPERSEDED"]; DEAD = [r for r in L if r["path_status"] == "SUPERSEDED"]
STALE = dict(MANUAL_STALE); STALE.update(build_stale(L))
for r in LIVE:
    add(r["value"], r["claim_id"])
    for m in re.findall(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", r["ci95"] or ""): add(m, r["claim_id"] + ".ci")
    add(r["n"], r["claim_id"] + ".n")
def harvest(o, src):
    if isinstance(o, dict):
        for k, v in o.items(): harvest(v, src)
    elif isinstance(o, (list, tuple)):
        for v in o: harvest(v, src)
    elif isinstance(o, (int, float)) and not isinstance(o, bool): add(o, src)
AD = R(CFG["artifacts_dir"]); KEY = CFG.get("harvest_root_key")
SRC = sorted(f[:-5] for f in os.listdir(AD) if f.endswith(".json")); skipped = [f for f in SRC if f in RETIRED]
for f in SRC:
    if f in RETIRED: print(f"  (폐기 제외) {f}: {RETIRED[f]}"); continue
    d = json.load(open(f"{AD}/{f}.json", encoding="utf-8")); harvest(d.get(KEY, {}) if KEY else d, f)
for fp in CFG.get("extra_artifact_files", []):
    if os.path.exists(R(fp)): harvest(json.load(open(R(fp), encoding="utf-8")), os.path.basename(fp)); SRC.append(fp)
    else: print(f"  (경고) 없음: {fp}")
for v, why in CFG.get("extra_constants", []): add(v, why)
print(f"산출물 {len(SRC)}개 · 허용 수치 {len(POOL):,}종 · 폐기 차단 {len(STALE)}종(수동 {len(MANUAL_STALE)} + 자동 {len(STALE)-len(MANUAL_STALE)}) · 원장 {len(LIVE)}행 유효/{len(DEAD)}행 폐기")
def figcap():
    src = CFG.get("caption_source")
    if not src or not os.path.exists(R(src)): return None
    for node in ast.walk(ast.parse(open(R(src), encoding="utf-8").read())):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == CFG.get("caption_var", "FIGCAP") for t in node.targets):
            return ast.literal_eval(node.value)
    return None
ITEMS = [(os.path.basename(p), open(R(p), encoding="utf-8").read()) for p in sys.argv[1:] or CFG["manuscripts"]]
cap = figcap()
if cap is not None and not sys.argv[1:]: ITEMS.append(("FIGCAP@" + os.path.basename(CFG["caption_source"]), cap))
ALLBAD, ALLSTALE = [], []
SKIP = CFG.get("skip_regex", r"Section \d(?:\.\d)?|Table \d|Figure \d[ab]?|column \(?\d\)?|Panel [A-H]|NBER Working Paper \d+|US\$\d+")
for name, txt in ITEMS:
    prose = txt.split(CFG.get("references_marker", "## References"))[0]
    prose = re.sub(r"^#{1,6} .*$", "", prose, flags=re.M); prose = re.sub(r"\|.*\|", "", prose)
    prose = prose.replace("−", "-").replace("–", "-"); prose = re.sub(r"(?<=\d),(?=\d{3}\b)", "", prose)
    prose = re.sub(r"\((?:19|20)\d\d[a-z]?\)", "", prose); prose = re.sub(r"\b(?:19|20)\d\d\b", "", prose); prose = re.sub(SKIP, "", prose)
    nums = sorted({round(float(m), 6) for m in re.findall(r"-?\d+(?:\.\d+)?", prose)})
    bad = [n for n in nums if n not in POOL]; stale = [(n, STALE[n]) for n in nums if n in STALE]
    print(f"  {name:<30} 고유 수치 {len(nums):>4} → 미확인 {len(bad)} {'✓' if not bad else '🔴 ' + str(bad[:6])}")
    for n, why in stale: print(f"      🔴 폐기 수치 {n} — {why}")
    ALLBAD += [(name, n) for n in bad]; ALLSTALE += [(name, n) for n, _ in stale]
print(f"\n총평: 대상 {len(ITEMS)} · 미확인 수치 {len(ALLBAD)} · 폐기 수치 {len(ALLSTALE)}")
sys.exit(1 if (ALLBAD or ALLSTALE) else 0)
