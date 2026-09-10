# -*- coding: utf-8 -*-
"""공개 전 안전 스캔 — 저장소 트리에서 (1) 10자리 사업자번호 (2) 회사명 패턴(주식회사·㈜·(주)·유한) (3) 절대 홈 경로
(4) 자격증명 키워드 (5) 지정 회사명 목록을 찾는다. exit 1 = 발견. 회사명 패턴은 정규식 코드(접미사 제거용)일 수 있으니
출력을 읽고 판단한다 — 자동 통과 없음.
사용: python3 safety_scan.py <repo-dir> [--names 회사명1 회사명2 ...] [--allow-regex "<허용 패턴>"]
"""
import os, re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--names", nargs="*", default=[]); ap.add_argument("--allow-regex", default=None)
a = ap.parse_args(); allow = re.compile(a.allow_regex) if a.allow_regex else None
hits = {"bizno10": [], "corp_suffix": [], "abs_path": [], "secret": [], "named_firm": []}; n = 0
for dp, dn, fs in os.walk(a.root):
    dn[:] = [d for d in dn if d not in (".git", "__pycache__", ".ipynb_checkpoints")]
    for f in fs:
        p = os.path.join(dp, f); n += 1
        if f.endswith((".png", ".pdf", ".jpg", ".parquet", ".pyc")): continue
        try: t = open(p, encoding="utf-8").read()
        except Exception: continue
        for i, ln in enumerate(t.split("\n"), 1):
            if allow and allow.search(ln): continue
            if re.search(r"(?<!\d)\d{10}(?!\d)", ln): hits["bizno10"].append(f"{p}:{i}")
            if re.search(r"주식회사|㈜|\(주\)|유한회사", ln): hits["corp_suffix"].append(f"{p}:{i}")
            if re.search(r"/mnt/" r"c/|/home/[a-z0-9_]+/|C:\\Users\\", ln): hits["abs_path"].append(f"{p}:{i}")
            if re.search(r"(?i)pass" r"word|passwd|api[_-]?key|secret[_-]?key|token=|NICEBIZ" r"LINE_PW", ln): hits["secret"].append(f"{p}:{i}")
            for nm in a.names:
                if nm and nm in ln: hits["named_firm"].append(f"{p}:{i} ({nm})")
print(f"files scanned {n}")
tot = 0
for k, v in hits.items():
    print(f"  {k:<12} {len(v)}"); [print("      ", x) for x in v[:8]]; tot += len(v)
sys.exit(1 if tot else 0)
