# -*- coding: utf-8 -*-
"""Build the three output-stored notebooks of the paper-VC repository.

The table and figure cells are **cut verbatim from code/build/p001_09_exhibits.py** — the script that generated the exhibits attached to the
manuscript — so the notebooks cannot drift from the paper's code. Each notebook ends with a consistency check against paper_exhibits/ that raises
if anything differs. Run from anywhere:  python code/build/make_notebooks.py"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_notebooks import build  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO); os.makedirs("notebooks", exist_ok=True); os.makedirs(os.path.join("figures", "tables"), exist_ok=True)
GEN = os.path.join("code", "build", "p001_09_exhibits.py")
src = open(GEN, encoding="utf-8").read().split("\n")
i_first_table = next(i for i, l in enumerate(src) if l.startswith('w("table1.md"'))
i_fig = next(i for i, l in enumerate(src) if l.startswith("# ---- Figures ----"))
header = "\n".join(src[:i_first_table])
header = header[header.index("import json"):]                                         # drop the module docstring
table_idx = [i for i, l in enumerate(src) if l.startswith('w("table')] + [i_fig]
table_blocks = ["\n".join(src[a:b]).rstrip() for a, b in zip(table_idx, table_idx[1:])]
fig_lines = src[i_fig + 1:]
fig_idx = [i for i, l in enumerate(fig_lines) if l.startswith("fig, ax = plt.subplots")] + [len(fig_lines)]
fig_blocks = ["\n".join(fig_lines[a:b]).rstrip() for a, b in zip(fig_idx, fig_idx[1:])]

COMMON = ["Every number below is read from an aggregate result artifact in `../artifacts/` — the same files the paper's tables and figures were generated from.",
          "No licensed microdata is used or required (see `../DATA_ACCESS.md`). Outputs are stored in this notebook, so everything renders on GitHub without running anything.",
          "The code cells are cut verbatim from `../code/build/p001_09_exhibits.py`; the last cell checks the result against `../paper_exhibits/`, the exhibits attached to the manuscript."]
SETUP = ('import os\n__file__ = os.path.abspath("../code/build/p001_09_exhibits.py")        # the generator locates the repository from its own path\n'
         'os.environ["P001_ARTIFACTS"] = os.path.abspath("../artifacts"); os.environ["P001_TABLES"] = os.path.abspath("../figures/tables"); os.environ["P001_FIGURES"] = os.path.abspath("../figures")\n'
         + header + '\nprint("artifacts loaded from", A)')


def tname(b):
    return re.search(r'w\("(table\w+\.md)"', b).group(1)


def ttitle(b):
    m = re.search(r'# (Table \d+\.[^\n]*)', b); return m.group(1) if m else tname(b)


# ── 01 tables ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
cells = [(["## Setup — imports, helpers and every artifact the generator reads (verbatim header of `p001_09_exhibits.py`)"], SETUP)]
for b in table_blocks:
    cells.append(([f"## {ttitle(b)}"], b + f'\n_md = open(os.path.join(OUT_T, "{tname(b)}"), encoding="utf-8").read()'))
ASSEMBLE = ('# The build step assembles tables.md: Tables 1–10 and Appendix Tables IA.1–IA.3 (verbatim: p001_09b_assemble_tables.py)\n'
            'import runpy, sys\nsys.argv = ["p001_09b_assemble_tables.py"]\nrunpy.run_path("../code/build/p001_09b_assemble_tables.py", run_name="__main__")\n'
            '_md = open("../figures/tables.md", encoding="utf-8").read()[:1200] + "\\n\\n…(truncated preview; the full file is ../figures/tables.md)"')
cells.append((["## Assembly — `tables.md` as attached to the manuscript (Unicode minus normalisation)"], ASSEMBLE))
CHECK_T = '''import glob, os
fails = 0
mine = sorted(glob.glob(os.path.join(OUT_T, "table*.md"))); ref_dir = "../paper_exhibits/tables"
for p in mine:
    a = open(p, encoding="utf-8").read(); b = open(os.path.join(ref_dir, os.path.basename(p)), encoding="utf-8").read()
    ok = a == b; fails += (not ok); print(f"{os.path.basename(p):<16} {'IDENTICAL' if ok else 'DIFFERS'}  ({len(a):,} chars)")
a = open("../figures/tables.md", encoding="utf-8").read(); b = open("../paper_exhibits/tables.md", encoding="utf-8").read()
ok = a == b; fails += (not ok); print(f"{'tables.md':<16} {'IDENTICAL' if ok else 'DIFFERS'}  ({len(a):,} chars; {a.count(chr(10) + '### ')} exhibits)")
assert len(mine) == len(glob.glob(os.path.join(ref_dir, "table*.md"))) == 13, "table count"
assert fails == 0, f"{fails} file(s) differ from the paper's exhibits"
print("\\nAll 11 generated table files and the assembled tables.md are byte-identical to the exhibits attached to the manuscript.")'''
cells.append((["## Consistency check — regenerated tables versus the paper's exhibits",
               "Byte-for-byte comparison of every generated table file and of the assembled `tables.md` with `../paper_exhibits/`. The cell raises if anything differs."], CHECK_T))
build("notebooks/01_tables.ipynb", "# Tables 1–10 and Appendix Tables IA.1–IA.3", COMMON, cells)

# ── 02 figures ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
FTITLES = {"figure1_ladder": "Figure 1 — Matching decomposition ladder (NA+EU)", "figure2_eventstudy": "Figure 2 — Female-partner arrivals and new-deal composition", "figure3_channel": "Figure 3 — Female-partner share by stage"}


def fname(b): return re.search(r'"(fig\w+)\.png"', b).group(1)


SETUP_F = ('import os\n__file__ = os.path.abspath("../code/build/p001_09_exhibits.py")\n'
           'os.environ["P001_ARTIFACTS"] = os.path.abspath("../artifacts"); os.environ["P001_TABLES"] = os.path.abspath("../figures/tables"); os.environ["P001_FIGURES"] = os.path.abspath("../figures")\n'
           '# The figures reuse quantities computed while the tables are built, so the generator is executed here up to its figure section (tables are regenerated silently into ../figures/tables).\n'
           '_src = open(__file__, encoding="utf-8").read().split("# ---- Figures ----")[0]\n'
           'import io, contextlib\nwith contextlib.redirect_stdout(io.StringIO()):\n    exec(compile(_src, __file__, "exec"))\n'
           'print("generator executed up to the figure section; artifacts from", A)')
cells = [(["## Setup — `p001_09_exhibits.py` executed up to its figure section (the figure cells below are its verbatim continuation)"], SETUP_F)]
pre = "\n".join(fig_lines[:fig_idx[0]]).strip("\n")
if pre.strip(): cells.append((["## Figure style (verbatim: the lines between the figure marker and the first figure)"], pre))
for b in fig_blocks: cells.append(([f"## {FTITLES.get(fname(b), fname(b))}"], b))
CHECK_F = '''import hashlib, os
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
fails = 0
for n in %s:
    a, b = sha(os.path.join(OUT_F, n + ".png")), sha(os.path.join("../paper_exhibits/figures", n + ".png"))
    ok = a == b; fails += (not ok); print(f"{n:<18} {'IDENTICAL' if ok else 'DIFFERS'}  sha256 {a[:16]}")
assert fails == 0, f"{fails} figure(s) differ from the paper"
print("\\nAll 3 figures are byte-identical to the paper's figure files.")''' % json.dumps([fname(b) for b in fig_blocks])
cells.append((["## Consistency check — regenerated figures versus the paper's figure files", "SHA-256 of each PNG just written to `../figures/` against the file attached to the manuscript."], CHECK_F))
build("notebooks/02_figures.ipynb", "# Figures 1–3", COMMON, cells)

# ── 03 traceability ────────────────────────────────────────────────────────────────────────────────────────────────────────
C1 = '''import json, os, csv
ART = "../artifacts"
rows = list(csv.DictReader(open(os.path.join(ART, "CLAIMS_LEDGER.csv"), encoding="utf-8-sig")))
def resolve(o, path):
    for k in [k for k in path.split(".") if k]:
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o
exact = derived = mismatch = missing = shawarn = 0; bad = []
for r in rows:
    f = os.path.join(ART, os.path.basename(r["source_json"]))
    if not os.path.exists(f):
        missing += 1; bad.append((r["claim_id"], "artifact not in repository", os.path.basename(r["source_json"]))); continue
    d = json.load(open(f, encoding="utf-8"))
    if r["sha256_16"] and d.get("sha256_16") and r["sha256_16"] != d["sha256_16"]: shawarn += 1
    try: o = resolve(d, r["json_path"])
    except Exception: mismatch += 1; bad.append((r["claim_id"], "path does not resolve", r["json_path"][:70])); continue
    if isinstance(o, (dict, list)): derived += 1; continue
    try: ok = abs(float(r["value"]) - float(o)) <= max(5e-5, abs(float(o)) * 1e-6)
    except Exception: ok = str(o) == r["value"]
    if ok: exact += 1
    else: mismatch += 1; bad.append((r["claim_id"], "value", f"{r['value']} vs {o}"))
print(f"ledger rows {len(rows)} · exact value match {exact} · object-valued (derived) rows {derived} · mismatches {mismatch} · artifact missing {missing} · script-hash warnings {shawarn}")
for b in bad[:20]: print("  ", b)
from collections import Counter
print("status:", dict(Counter(r["path_status"] for r in rows)))
assert mismatch == 0 and missing == 0, "ledger does not resolve against the artifacts"'''
C2 = '''import hashlib, csv
man = list(csv.DictReader(open("../ARTIFACT_MANIFEST.csv", encoding="utf-8")))
bad = [m["file"] for m in man if hashlib.sha256(open(os.path.join(ART, m["file"]), "rb").read()).hexdigest()[:16] != m["sha256_16"]]
print(f"artifacts in manifest {len(man)} · hash mismatches {len(bad)}", bad[:5])
assert not bad
cited = sum(int(m["ledger_rows"]) > 0 for m in man); gen = sum(m["read_by_exhibit_generator"] == "yes" for m in man)
print(f"artifacts cited by the ledger {cited} · read by the exhibit generator {gen}")'''
C3 = '''runs = list(csv.DictReader(open(os.path.join(ART, "run_log.csv"), encoding="utf-8-sig")))
print(f"harness runs logged: {len(runs)}")
for r in runs[-8:]: print(f"  {r['run_id']:<9} {r['date']}  {r['script']:<44} {r['verdict']}")'''
cells = [(["## Claims ledger → artifacts", "Every row of `CLAIMS_LEDGER.csv` names an artifact file and a JSON path; this cell resolves each and compares the stored value (tolerance 5e-5 or 1e-6 relative). Object-valued rows point at whole result blocks (a table row, a CI pair) and are reported as derived."], C1),
         (["## Artifact hashes → manifest", "`ARTIFACT_MANIFEST.csv` records the SHA-256 prefix of every artifact at assembly time."], C2),
         (["## Run log", "One row per harness run, with the SHA-256 prefix of the script as run."], C3)]
build("notebooks/03_traceability.ipynb", "# Traceability: ledger, artifacts, manifest, run log", COMMON[:1] + ["This notebook reads only `../artifacts/` and `../ARTIFACT_MANIFEST.csv`."], cells)
print("notebooks built")
