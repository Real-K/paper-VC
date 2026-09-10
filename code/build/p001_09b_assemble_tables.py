# -*- coding: utf-8 -*-
"""tables.md 조립 (v8): Table 1–10 + Appendix Table IA.1–IA.3 — 생성기가 최종 번호로 파일을 쓴다(재배치 없음). 버전 스탬프; 음수 부호 U+2212 정규화."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
T = os.environ.get("P001_TABLES", os.path.join(REPO, "figures", "tables"))
stamp = sys.argv[1] if len(sys.argv) > 1 else "W5 v8 (2026-09-10, post external review)"
parts = [f"*{stamp}; regenerated from P001-02 … P001-60 and I-73 … I-82 via `06_code/p001_09_exhibits.py`; assembled by the build step. Do not edit by hand.*"]


def read_lines(fn):
    return io.open(os.path.join(T, fn), encoding="utf-8").read().rstrip("\n").split("\n")


for n in range(1, 11):
    lines = read_lines(f"table{n}.md")
    parts.append(f"### Table {n}. {re.sub(r'^Table\s+\d+\.\s*', '', lines[0].lstrip('#').strip())}\n" + "\n".join(lines[1:]))
for k in (1, 2, 3):
    lines = read_lines(f"tableIA{k}.md")
    parts.append(f"### Appendix Table IA.{k}. {re.sub(r'^Appendix Table IA\.\d\.\s*', '', lines[0].lstrip('#').strip())}\n" + "\n".join(lines[1:]))
out = "\n\n".join(parts) + "\n"
out = re.sub(r"(?<=[\s|\[(])-(?=\d)", "\u2212", out)
io.open(os.path.join(os.path.dirname(T), "tables.md"), "w", encoding="utf-8", newline="\n").write(out)
print(f"tables.md 조립: 10 본문 표 + 3 부록 표 (스탬프: {stamp})")
