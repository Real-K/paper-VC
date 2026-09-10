# -*- coding: utf-8 -*-
"""상호참조 해석기 + 그림 캡션 검사. 절·표·그림·부록 참조가 실제 대상을 가리키는지, 캡션 번호가 중복·누락 없이
실제 그림 제목·FIGS 제목과 일치하는지 확인한다. 표 재번호처럼 **수치를 바꾸지 않는 변경**은 수치 검증기를 통과하므로 별도 축.
설정 키: main_manuscript, manuscripts, appendix, tables_md, appendix_tables_md, exhibits_dir, caption_source, exhibits_source
"""
import os, re, sys, json, ast
CFG_PATH = os.environ.get("VERIFY_CONFIG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_config.json")
CFG = json.load(open(CFG_PATH, encoding="utf-8")); ROOT = os.path.dirname(os.path.abspath(CFG_PATH))
R = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))
def heads(p): return [l.rstrip() for l in open(R(p), encoding="utf-8") if l.startswith("#")] if p and os.path.exists(R(p)) else []
secs, subs, apps, tabs, atabs, figs, afigs = set(), set(), set(), set(), set(), set(), set()
for h in heads(CFG["main_manuscript"]):
    m = re.match(r"##\s+(\d+)\.\s", h);        secs.add(m.group(1)) if m else None
    m = re.match(r"###\s+(\d+\.\d+)\s", h);    subs.add(m.group(1)) if m else None
    m = re.match(r"##\s+Appendix\s+([A-Z])\.", h); apps.add(m.group(1)) if m else None
for h in heads(CFG.get("appendix")):
    m = re.match(r"##\s+([A-Z])\.\s", h);      apps.add(m.group(1)) if m else None
    m = re.match(r"###\s+([A-Z]\.\d+[a-z]?)\s", h); apps.add(m.group(1)) if m else None
for h in heads(CFG.get("tables_md")):
    m = re.match(r"###\s+Table\s+(\d+)\.", h); tabs.add(m.group(1)) if m else None
for h in heads(CFG.get("appendix_tables_md")):
    m = re.match(r"###\s+Appendix Table\s+([A-Z]\.\d+(?:\.\d+)*)\.", h); atabs.add(m.group(1)) if m else None
EX = R(CFG["exhibits_dir"]) if CFG.get("exhibits_dir") else None
if EX and os.path.isdir(EX):
    for f in os.listdir(EX):
        m = re.match(r"figure(A?\d+)_.*\.png$", f)
        if m: (afigs if m.group(1).startswith("A") else figs).add(m.group(1))
print(f"대상: 절 {len(secs)} · 소절 {len(subs)} · 부록 {sorted(apps)} · 표 {sorted(tabs, key=int)} · 부록표 {sorted(atabs)} · 그림 {sorted(figs)} + {sorted(afigs)}")
PATS = [(re.compile(r"Appendix Table\s+([A-Z]\.\d+(?:\.\d+)*)"), lambda v: v in atabs, "부록표"),
        (re.compile(r"Appendix (?:Figure )?([A-Z]\d+)\b"), lambda v: v in afigs, "부록그림"),
        (re.compile(r"Appendix\s+([A-Z]\.\d+[a-z]?)\b"), lambda v: v in apps, "부록절"),
        (re.compile(r"Appendix\s+([A-Z])\b(?![.\w])"), lambda v: v in apps, "부록"),
        (re.compile(r"\bTable\s+(\d+)\b"), lambda v: v in tabs, "표"),
        (re.compile(r"\bFigure\s+(\d+)\b"), lambda v: v in figs, "그림"),
        (re.compile(r"\bSections?\s+(\d+\.\d+)\b"), lambda v: v in subs, "소절"),
        (re.compile(r"\bSections?\s+(\d+)\b(?!\.\d)"), lambda v: v in secs, "절")]
def _assign(src, name):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == name for t in node.targets): return ast.literal_eval(node.value)
def _norm(t): return re.sub(r"\s+", " ", t).strip().rstrip(".")
def exhibit_titles():
    out = {}
    if not CFG.get("exhibits_source") or not os.path.exists(R(CFG["exhibits_source"])): return out
    for node in ast.walk(ast.parse(open(R(CFG["exhibits_source"]), encoding="utf-8").read())):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") in ("suptitle", "set_title") and node.args:
            a = node.args[0]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                m = re.match(r"Figure ([A-Z]?\d+)\. (.*)", a.value.strip(), re.S)
                if m: out[m.group(1)] = _norm(m.group(2))
    return out
def check_captions():
    src_p = CFG.get("caption_source")
    if not src_p or not os.path.exists(R(src_p)): return None
    src = open(R(src_p), encoding="utf-8").read(); figs_l, figcap = _assign(src, CFG.get("figs_var", "FIGS")), _assign(src, CFG.get("caption_var", "FIGCAP"))
    if not figs_l or not figcap: return [("FIGS/FIGCAP", "읽지 못함", "")]
    bad = []; caps = re.findall(r"\*\*Figure ([A-Z]?\d+)\. (.*?)\*\*", figcap, re.S); nums = [n for n, _ in caps]
    for n in {x for x in nums if nums.count(x) > 1}: bad.append(("캡션 중복", f"Figure {n}", ""))
    files = figs | afigs
    for n in sorted(files - set(nums)): bad.append(("캡션 누락", f"Figure {n}", "그림은 있으나 캡션 없음"))
    for n in sorted(set(nums) - files): bad.append(("그림 없음", f"Figure {n}", "캡션은 있으나 그림 없음"))
    real = exhibit_titles(); ft = {}
    for _, t in figs_l:
        m = re.match(r"Figure ([A-Z]?\d+)\. (.*)", t, re.S)
        if m: ft[m.group(1)] = _norm(m.group(2))
    for n, t in caps:
        if n in real and _norm(t) != real[n]: bad.append(("제목 불일치(캡션↔그림)", f"Figure {n}", f"캡션 '{_norm(t)[:60]}' vs 그림 '{real[n][:60]}'"))
        if n in ft and _norm(t) != ft[n]: bad.append(("제목 불일치(캡션↔FIGS)", f"Figure {n}", f"FIGS '{ft[n][:60]}'"))
    key = lambda n: (0, int(n)) if n.isdigit() else (1, int(n[1:]))
    if nums != sorted(nums, key=key): bad.append(("순서", " ".join(nums), "본문 그림 → 부록 그림"))
    for ln in figcap.split("\n"):
        if ln.startswith("#"): continue
        for pat, ok, lab in PATS:
            for m in pat.finditer(ln):
                if not ok(m.group(1)): bad.append((f"캡션 참조 {lab}", m.group(0), ln.strip()[:90]))
    return bad
targets = sys.argv[1:] or [p for p in CFG["manuscripts"] + [CFG.get("appendix"), CFG.get("tables_md"), CFG.get("appendix_tables_md")] if p]
bad = 0
for t in targets:
    hits = []; inref = False
    for i, ln in enumerate(open(R(t), encoding="utf-8"), 1):
        if re.match(r"#+\s*References", ln): inref = True
        if inref or ln.startswith("#"): continue
        for pat, ok, lab in PATS:
            for m in pat.finditer(ln):
                if not ok(m.group(1)): hits.append((i, lab, m.group(0), ln.strip()[:100]))
    bad += len(hits); print(f"  {os.path.basename(t):<28} 미해결 {len(hits)} {'✓' if not hits else '🔴'}")
    for i, lab, ref, ctx in hits[:40]: print(f"      L{i:<4} {lab} '{ref}' — {ctx}")
cap = check_captions()
if cap is not None:
    print(f"  {'FIGCAP':<28} 문제 {len(cap)} {'✓' if not cap else '🔴'}")
    for k, w, c in cap[:40]: print(f"      {k} '{w}' — {c}")
print(f"\n총평: 미해결 참조 {bad}건 · 캡션 문제 {len(cap or [])}건"); sys.exit(1 if (bad or cap) else 0)
