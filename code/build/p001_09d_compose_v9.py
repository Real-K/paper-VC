# -*- coding: utf-8 -*-
"""v9 표 조립 (2026-09-10; 리뷰 c1·c2·c3): 생성기(p001_09_exhibits.py)가 tables/components/ 에 쓴 블록을 최종 번호의 표로 합친다.

최종 전시물
  Table 1 표본·측정 범위(+모집단 규칙·고유 단위·투자자 유형·직책)        Table 2 매칭 사다리 (A) + 공동귀속·공통 support (B)
  Table 3 단계 편향                                                        Table 4 순위 회계·성별 평균 백분위·벤치마크 불확실성 (신규)
  Table 5 출구 격차의 위치 (옛 Table 4)                                   Table 6 균형 (옛 Table 6)
  Table 7 파트너 내 검정 + 지평 사다리·짝지은 차이·two-way FE (옛 Table 5B)  Table 8 정보량 (옛 Table 7 D1·D2·E) + Mundlak within/between (C)
  IA.1 전체 사양 사다리 · IA.2 강건성·측정 진단 · IA.3 이동·부재·파이프라인 · IA.4 딜 고정(옛 T8) · IA.5 자금조달 사다리(옛 T9) ·
  IA.6 영입·이탈(옛 T10) · IA.7 후속 딜 활동·경력·함의 기여(옛 T7 B·C·E 일부) · IA.8 모집단 점검 · IA.9 공변량 조정 해저드·배터리(옛 T5 A·C)
교차참조는 옛 번호 → 새 번호로 치환한다(자리표시자 경유; 연쇄 치환 방지).
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
C = os.environ.get("P001_TABLES", os.path.join(REPO, "figures", "tables", "components"))          # generator components
T = os.environ.get("P001_TABLES_FINAL", os.path.dirname(C.rstrip("/\\")))                               # final numbered tables
os.makedirs(T, exist_ok=True)


def rd(fn):
    return io.open(os.path.join(C, fn), encoding="utf-8").read().rstrip("\n")


def wr(fn, txt):
    io.open(os.path.join(T, fn), "w", encoding="utf-8", newline="\n").write(txt.rstrip("\n") + "\n"); print("final:", fn)


def panels(txt):
    """'## Panel X.' 로 시작하는 블록으로 분할; [0] 은 제목·서문."""
    parts = re.split(r"(?m)^(?=## Panel )", txt)
    return parts[0], parts[1:]


def retitle(txt, title):
    lines = txt.split("\n"); assert lines[0].startswith("# "), lines[0]; lines[0] = "# " + title; return "\n".join(lines)


def relabel(block, new_letter):
    return re.sub(r"^## Panel [A-E][0-9]?\.", f"## Panel {new_letter}.", block, count=1, flags=re.M)


def strip_rows(block, prefixes):
    keep = [l for l in block.split("\n") if not any(l.startswith(p) for p in prefixes)]
    return "\n".join(keep)


def only_rows(block, prefixes):
    return [l for l in block.split("\n") if any(l.startswith(p) for p in prefixes)]


# ── Table 1 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
t1 = rd("table1.md"); extra = rd("t1_extra.md")
i = t1.rfind("\n\n*Sources"); assert i > 0
t1 = t1[:i].rstrip("\n") + "\n" + extra + t1[i:]
wr("table1.md", t1)

# ── Table 2 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
t2 = rd("table2.md"); lines = t2.split("\n")
t2 = lines[0] + "\n## Panel A. Decomposition ladder: firm × year cells, adding sector, adding stage\n" + "\n".join(lines[1:])
wr("table2.md", t2 + "\n\n" + rd("t2_panelB.md"))

# ── Table 3 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
wr("table3.md", rd("table3.md"))

# ── Table 4 (new) ──────────────────────────────────────────────────────────────────────────────────────────────────────
wr("table4.md", rd("t4_rank.md"))

# ── Table 5 (old Table 4) ──────────────────────────────────────────────────────────────────────────────────────────────
wr("table5.md", retitle(rd("table4.md"), "Table 5. Where the exit gap lives: female-founded deals across comparison sets, and the cross-deal information each retains"))

# ── Table 6 ────────────────────────────────────────────────────────────────────────────────────────────────────────────
wr("table6.md", retitle(rd("table6.md"), "Table 6. Balance of company characteristics within the cells that identify the peer comparison (female-founded deals, firm × year × sector; deals through 2017-10)"))

# ── Table 7 (old Table 5, Panel B) + horizon rows ──────────────────────────────────────────────────────────────────────
head5, p5 = panels(rd("table5.md")); assert len(p5) == 3, len(p5)
pB = p5[1]
hz = rd("t7_horizon.md")
anchor = "| &nbsp;&nbsp;follow-on financing within 36 months |"
k = pB.find(anchor); assert k > 0
eol = pB.find("\n", k)
pB = pB[:eol + 1] + hz + "\n" + pB[eol + 1:]
# split-sample vintage difference row (P001-60 B2) sits right after the pooled vintage-contrast rows
vint = rd("t7_vintage_split.md") if os.path.exists(os.path.join(C, "t7_vintage_split.md")) else ""
if vint:
    a2 = "| Vintage contrast, 36-month exit (deals through 2020-10)"; k2 = pB.find(a2); assert k2 > 0; e2 = pB.find("\n", k2)
    pB = pB[:e2 + 1] + vint + "\n" + pB[e2 + 1:]
pB = relabel(pB, "A").replace("## Panel A. Within-partner outcome test:", "## Panel A. Estimates:", 1)
t7 = ("# Table 7. Within-partner outcome test: female-founded versus other deals of the same partner, by partner gender, across horizons (NA+EU)\n"
      "Outcome: the deal's exit (or follow-on) indicator net of the leave-one-out mean of its year × sector × stage market cell; partner fixed effects and deal controls. "
      "β_int is the difference between female and male partners' own female-founded − other gaps.\n\n" + pB)
wr("table7.md", t7)

# ── Table 8 (old Table 7 D1·D2·E + Mundlak) ───────────────────────────────────────────────────────────────────────────
head7, p7 = panels(rd("table7.md")); assert len(p7) == 6, len(p7)   # A, B, C, D1, D2, E
pD1, pD2, pE = p7[3], p7[4], p7[5]
implied_prefix = ("| Implied contribution of composition", "| Same, fixed 36-month exit horizon")
implied_rows = only_rows(pE, implied_prefix)
pE = strip_rows(pE, implied_prefix)
note7 = head7[head7.find("\n*"):] if "\n*" in head7 else ""
# the note of the old Table 7 lives at the end of Panel E
if "\n*Partners with" in pE:
    j = pE.rfind("\n*Partners with"); note_all = pE[j:]; pE = pE[:j]
else:
    note_all = ""
t8 = ("# Table 8. Does the composition component carry information about later performance? (NA+EU partners with at least five attributed deals through 2017-10)\n\n"
      + relabel(pD1, "A").replace("## Panel A. Does composition carry information? Open horizon", "## Panel A. Open horizon", 1)
      + relabel(pD2, "B").replace("## Panel B. Same question at a fixed 36-month exit horizon in both periods", "## Panel B. Fixed 36-month exit horizon in both periods", 1)
      + relabel(rd("t8_mundlak.md"), "C") + "\n\n"
      + relabel(pE, "D") + note_all.replace("Panel D1 and Panel E percentile-scale rows", "Panel A and Panel D percentile-scale rows").replace("Panel D2's control set", "Panel B's control set")
      .replace("Panel D2 rows below the preferred row", "Panel B rows below the preferred row").replace("Panels B–E: deal-count and gender controls (Panel B additionally pre-period early-stage share and sector breadth)", "Panels A, B and D: deal-count and gender controls")
      .replace("Panel B's negative value is that composition coefficient.", "Appendix Table IA.7, Panel A's negative value is that composition coefficient."))
wr("table8.md", t8)

# ── Appendix tables ────────────────────────────────────────────────────────────────────────────────────────────────────
ia1 = rd("tableIA1.md").replace("Full specification ladders (Table 7, Panels D1 and D2)", "Full specification ladders (Table 8, Panels A and B)").replace("Same construction, samples, and sources as Table 7; see its note.", "Same construction, samples, and sources as Table 8; see its note.")
ia1 = ia1.replace("## Panel D1. Does composition carry information? Open horizon", "## Panel A. Open horizon").replace("## Panel D2. Same question at a fixed 36-month exit horizon in both periods", "## Panel B. Fixed 36-month exit horizon in both periods")
wr("tableIA1.md", ia1)
ia2 = rd("tableIA2.md")
ia2 = ia2.replace("## Panel B. Covariate-adjusted follow-on estimates across specifications", "## Panel B. Follow-on estimates across specifications (cell-demeaned within-cell estimator; the 'baseline' row carries no deal controls, which is why it differs from the covariate-adjusted battery of Appendix Table IA.9, Panel B)")
wr("tableIA2.md", ia2)
wr("tableIA3.md", rd("tableIA3.md"))
wr("tableIA4.md", retitle(rd("table8.md"), "Appendix Table IA.4. The deal held fixed: within-round comparison of co-investors on female-founded rounds (NA+EU)"))
wr("tableIA5.md", retitle(rd("table9.md"), "Appendix Table IA.5. The female-partner channel along the financing ladder (NA+EU)"))
wr("tableIA6.md", retitle(rd("table10.md"), "Appendix Table IA.6. Partner turnover and deal composition: deal-level stacked event studies (NA+EU)"))
pB7, pC7 = p7[1], p7[2]
ia7 = ("# Appendix Table IA.7. Subsequent attributed deal activity, career margins, and the implied composition contribution to the gender gap (NA+EU partners with at least five attributed deals through 2017-10)\n\n"
       + relabel(pB7, "A") + relabel(pC7, "B")
       + "## Panel C. Implied contribution of female partners' composition to the female − male difference in post-period within-cell performance (levels; Σ tenure-controlled part gap × tenure-controlled coefficient, same resamples)\n| Horizon | β | 95% CI | n |\n|---|---|---|---|\n" + "\n".join(implied_rows)
       + "\n\n*Panel A: deal-count and gender controls plus pre-period early-stage share and sector breadth; investor-firm cluster bootstrap. Panel C is a model-conditional implied contribution (common linear slopes across genders; tenure controls), reported against a ±2-point materiality band for this channel. Sources: P001-18b, P001-23, P001-25, P001-29, P001-36, P001-38.*")
wr("tableIA7.md", ia7)
wr("tableIA8.md", rd("tableIA8.md"))
pA5, pC5 = p5[0], p5[2]
ia9 = ("# Appendix Table IA.9. Covariate-adjusted exit hazard and outcome battery on the peer-comparison cells (NA+EU)\n\n" + relabel(pA5, "A") + relabel(pC5, "B"))
wr("tableIA9.md", ia9)

# ── prune stale finals (v8 numbering left table9/table10 behind; the v9 set is the only truth) ─────────────────────────
FINAL = {f"table{k}.md" for k in range(1, 9)} | {f"tableIA{k}.md" for k in range(1, 10)}
for fn in sorted(os.listdir(T)):
    if fn.startswith("table") and fn.endswith(".md") and fn not in FINAL:
        os.remove(os.path.join(T, fn)); print("pruned stale exhibit:", fn)
assert {fn for fn in os.listdir(T) if fn.startswith("table") and fn.endswith(".md")} == FINAL, "final table set mismatch"
FIG = os.environ.get("P001_FIGURES", os.path.join(REPO, "figures"))
_want = {"figure1_ladder.png", "figure2_rank_change.png", "figure3_horizon.png", "figureA1_eventstudy.png", "figureA2_channel.png"}
_have = {f for f in os.listdir(FIG) if f.endswith(".png")} if os.path.isdir(FIG) else set()
if _have:                                                  # 그림이 이미 생성된 트리에서만 점검(표만 만드는 실행에서는 건너뜀)
    for fn in sorted(_have - _want):
        os.remove(os.path.join(FIG, fn)); print("pruned stale figure:", fn)
    assert _want <= _have, f"missing figures: {sorted(_want - _have)}"

# ── cross-reference renumbering (old v8 numbering → v9) ─────────────────────────────────────────────────────────────────
MAP = [  # order matters; placeholders prevent chained replacement
    ("Appendix Table IA.2, Panel E", "Appendix Table IA.2, Panel E"), ("Appendix Table IA.2, Panel D", "Appendix Table IA.2, Panel D"),
    ("Table 7 Panel D2 preferred specification", "Table 8, Panel B, preferred specification"), ("Table 7 Panel C uses", "Appendix Table IA.7, Panel B, uses"),
    ("Table 7, Panels D1 and D2", "Table 8, Panels A and B"), ("Table 10", "Appendix Table IA.6"), ("Table 9", "Appendix Table IA.5"), ("Table 8", "Appendix Table IA.4"),
    ("Table 5, Panel A", "Appendix Table IA.9, Panel A"), ("Table 5, Panel B", "Table 7"), ("Table 4 hazard", "Appendix Table IA.9 hazard"), ("Table 4 cells", "Table 5 cells"),
    ("Table 3 peer comparison", "Table 5 peer comparison"), ("Table 4, Panel B", "Table 5, Panel B"), ("Table 4", "Table 5"), ("Table 7", "Table 8"),
]
for fn in sorted(os.listdir(T)):
    if not (fn.startswith("table") and fn.endswith(".md")): continue
    p = os.path.join(T, fn); s = io.open(p, encoding="utf-8").read(); s0 = s
    title = s.split("\n", 1)[0]; body = s[len(title):]
    for k, (old, new) in enumerate(MAP):
        body = body.replace(old, f"\x00{k}\x00")
    for k, (old, new) in enumerate(MAP):
        body = body.replace(f"\x00{k}\x00", new)
    s = title + body
    if s != s0: io.open(p, "w", encoding="utf-8", newline="\n").write(s); print("  renumbered refs in", fn)
print("compose v9 done")
