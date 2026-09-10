# -*- coding: utf-8 -*-
"""Render every pipeline / public-source / build script as a read-only Jupyter notebook (no outputs) under notebooks/pipeline/.

Cells are cut at the module docstring (→ a Markdown cell) and at section-marker comments (`# ──`, `# ══`, `# ----`, `# ====`, `# ── A.`),
so the notebook shows the same code as the .py file in readable blocks. Nothing is executed: these scripts need the licensed inputs.
Run from anywhere:  python code/build/py_to_ipynb.py"""
import ast
import glob
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(REPO, "notebooks", "pipeline"); os.makedirs(OUT, exist_ok=True)
MARK = re.compile(r"^# [─═\-=]{3,}|^# ── |^# ---- ")


def to_nb(path, rel):
    src = open(path, encoding="utf-8").read()
    try:
        doc = ast.get_docstring(ast.parse(src))
    except SyntaxError:
        doc = None
    cells = [{"cell_type": "markdown", "metadata": {}, "source": [f"# `{rel}`\n", "\n", "Read-only rendering of the script (no outputs; it needs the licensed inputs described in `../../DATA_ACCESS.md`). The .py file is the version of record.\n"]}]
    if doc:
        cells.append({"cell_type": "markdown", "metadata": {}, "source": ["```text\n"] + [l + "\n" for l in doc.split("\n")] + ["```\n"]})
        body = src.split('"""', 2)[2] if src.count('"""') >= 2 else src
    else:
        body = src
    lines = body.split("\n"); idx = [0] + [i for i, l in enumerate(lines) if MARK.match(l) and i > 0] + [len(lines)]
    for a, b in zip(idx, idx[1:]):
        block = "\n".join(lines[a:b]).strip("\n")
        if block.strip(): cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "source": [l + "\n" for l in block.split("\n")], "outputs": []})
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": sys.version.split()[0]}}, "nbformat": 4, "nbformat_minor": 5}
    out = os.path.join(OUT, os.path.splitext(os.path.basename(path))[0] + ".ipynb")
    json.dump(nb, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(cells)


n = 0
for sub in ("pipeline", "public_sources", "build"):
    for p in sorted(glob.glob(os.path.join(REPO, "code", sub, "*.py"))):
        if os.path.basename(p) in ("build_notebooks.py", "make_notebooks.py", "py_to_ipynb.py"): continue
        to_nb(p, f"code/{sub}/{os.path.basename(p)}"); n += 1
print(f"notebooks/pipeline: {n} notebooks")
