# -*- coding: utf-8 -*-
"""tables.md 조립 (v9): Table 1–8 + Appendix Table IA.1–IA.9 — p001_09d_compose_v9.py 가 최종 번호로 파일을 쓴다. 버전 스탬프; 음수 부호 U+2212 정규화."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
T = os.environ.get("P001_TABLES_FINAL", os.path.join(REPO, "figures", "tables"))
stamp = sys.argv[1] if len(sys.argv) > 1 else "W5 v9 (2026-09-10, sample_v2 rebuild; reviews c1–c3)"
parts = [f"*{stamp}; regenerated from P001-00 … P001-63 and I-73 … I-82 via `06_code/p001_09_exhibits.py` and `p001_09d_compose_v9.py`; assembled by the build step. Do not edit by hand.*"]


def read_lines(fn):
    return io.open(os.path.join(T, fn), encoding="utf-8").read().rstrip("\n").split("\n")


for n in range(1, 9):
    lines = read_lines(f"table{n}.md")
    parts.append(f"### Table {n}. {re.sub(r'^Table\s+\d+\.\s*', '', lines[0].lstrip('#').strip())}\n" + "\n".join(lines[1:]))
for k in range(1, 10):
    lines = read_lines(f"tableIA{k}.md")
    parts.append(f"### Appendix Table IA.{k}. {re.sub(r'^Appendix Table IA\.\d\.\s*', '', lines[0].lstrip('#').strip())}\n" + "\n".join(lines[1:]))
out = "\n\n".join(parts) + "\n"
out = re.sub(r"(?<=[\s|\[(])-(?=\d)", "\u2212", out)
io.open(os.path.join(os.path.dirname(T), "tables.md"), "w", encoding="utf-8", newline="\n").write(out)
print(f"tables.md 조립: 8 본문 표 + 9 부록 표 (스탬프: {stamp})")
