# -*- coding: utf-8 -*-
"""tables.md 조립 (v7.1): Table 1–8 + Table 9 (= 생성 table10 Panels A–B) + Appendix Table IA.1 · IA.2 (= 생성 table9) · IA.3 (= 생성 table10 Panels C–E → A–C).
버전 스탬프 (R4 writing finding 20); 음수 부호 정규화 U+2212 (R6 writing W-27); 재배치는 JFQA 40–45 pdf 페이지 한도(R6 W-46) — 생성기 산출물은 그대로 두고 조립 단계에서 재번호."""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
T = os.environ.get("P001_TABLES", os.path.join(REPO, "figures", "tables"))
stamp = sys.argv[1] if len(sys.argv) > 1 else "W5 v7.1 (2026-09-10, post R6)"
MAP_CDE = {"C": "A", "D": "B", "E": "C"}


def read_lines(fn):
    return io.open(os.path.join(T, fn), encoding="utf-8").read().rstrip("\n").split("\n")


def title_of(line, prefix_re):
    return re.sub(prefix_re, "", line.lstrip("#").strip())


parts = [f"*{stamp}; regenerated from P001-02 … P001-59 and I-73 … I-82 via `06_code/p001_09_exhibits.py`; assembled by the build step (Table 9 = generated table10 A–B; Appendix Tables IA.2 = generated table9, IA.3 = generated table10 C–E). Do not edit by hand.*"]
for n in range(1, 9):
    lines = read_lines(f"table{n}.md")
    parts.append(f"### Table {n}. {title_of(lines[0], r'^Table\s+\d+\.\s*')}\n" + "\n".join(lines[1:]))
# generated table10 → Table 9 (Panels A–B) and Appendix Table IA.3 (Panels C–E → A–C)
t10 = read_lines("table10.md"); body10 = "\n".join(t10[1:])
k = body10.find("## Panel C."); assert k > 0, "table10 Panel C not found"
ab, cde = body10[:k].rstrip("\n"), body10[k:]
parts.append("### Table 9. Additional designs: the deal held fixed and the undiluted balance of the identifying cells\n" + ab)
ia1 = read_lines("tableIA1.md")
ia_parts = [f"### Appendix Table IA.1. {title_of(ia1[0], r'^Appendix Table IA\.1\.\s*')}\n" + "\n".join(ia1[1:])]
t9 = read_lines("table9.md")
ia_parts.append(f"### Appendix Table IA.2. {title_of(t9[0], r'^Table\s+9\.\s*')}\n" + "\n".join(t9[1:]))
cde = re.sub(r"^## Panel ([CDE])\.", lambda m: f"## Panel {MAP_CDE[m.group(1)]}.", cde, flags=re.M)
ia_parts.append("### Appendix Table IA.3. Movers, absences, and the financing-ladder pipeline\n" + cde)
out = "\n\n".join(parts + ia_parts) + "\n"
# cross-references inside table notes follow the same renumbering
out = re.sub(r"Table 9, Panel ([A-E])", r"Appendix Table IA.2, Panel \1", out)
out = re.sub(r"(?<!Appendix Table IA\.2\. )(?<!### )Table 9\b(?!, Panel)(?! =)", "Appendix Table IA.2", out)
out = re.sub(r"Table 10, Panel ([CDE])", lambda m: f"Appendix Table IA.3, Panel {MAP_CDE[m.group(1)]}", out)
out = re.sub(r"Table 10, Panel ([AB])", r"Table 9, Panel \1", out)
out = re.sub(r"(?<!generated )Table 10\b", "Table 9", out)
# R6 writing W-27: one minus sign (U+2212) for every negative number in the assembled tables
out = re.sub(r"(?<=[\s|\[(])-(?=\d)", "\u2212", out)
io.open(os.path.join(os.path.dirname(T), "tables.md"), "w", encoding="utf-8", newline="\n").write(out)
print(f"tables.md 조립: {len(parts) - 1} 본문 표 + {len(ia_parts)} 부록 표 (스탬프: {stamp})")
