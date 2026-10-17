"""Tests A and B - integrity of the published notebook and data.

A (code): for every code cell, the token stream without comments and the AST must equal those of
  the original notebook; cell count/order/types, outputs, execution counts and metadata must be
  unchanged; markdown cells may differ only in translated text (embedded images unchanged).
B (data): SHA-256, rows, columns, column names and dtypes of every data file.

The reference fingerprints in tests/reference/ were generated from the ORIGINAL files.
  python tests/check_integrity.py                      # compare with the stored reference
  python tests/check_integrity.py --original DIR       # also compare directly with the originals
  python tests/check_integrity.py --write-reference DIR  (maintainers only)
DIR is the folder holding the original 'AI Comfort.ipynb' and 'database/'.
"""
import argparse
import ast
import hashlib
import io
import json
import re
import sys
import tokenize
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "AI Comfort.ipynb"
DATA = ROOT / "data"
REF = ROOT / "tests" / "reference" / "fingerprint.json"
DATA_FILES = ["db_obj.csv", "db_sub.csv", "db_validation.csv", "Dicionário.xlsx"]


def lp(p):
    """Long-path-safe string for Windows (paths over 260 characters)."""
    s = str(Path(p).resolve())
    return "\\\\?\\" + s if sys.platform == "win32" and not s.startswith("\\\\?\\") else s


def sha256(p):
    return hashlib.sha256(open(lp(p), "rb").read()).hexdigest()


def mask(src):
    """IPython shell/magic lines (!pip, %matplotlib) are not Python: keep them as opaque comments."""
    return "\n".join(("#MAGIC " + l) if l.lstrip().startswith(("!", "%")) else l for l in src.split("\n"))


def docstring_nodes(tree):
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            b = n.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) \
                    and isinstance(b.value.value, str):
                yield n, b


def code_fingerprint(src):
    """Executable fingerprint (comments and docstrings excluded) plus the docstrings themselves.
    Docstrings are documentation: they are compared separately and reported, not hidden."""
    masked = mask(src)
    tree = ast.parse(masked)
    doc_starts, docstrings = set(), []
    for owner, b in docstring_nodes(tree):
        doc_starts.add((b.lineno, b.col_offset))
        docstrings.append([owner.name, b.value.value])
        b.value.value = ""                                   # neutralise for the executable AST
    toks = [(t.type, t.string) for t in tokenize.generate_tokens(io.StringIO(masked).readline)
            if t.type not in (tokenize.COMMENT, tokenize.NL, tokenize.ENCODING)
            and not (t.type == tokenize.STRING and t.start in doc_starts)]
    magics = [l for l in src.split("\n") if l.lstrip().startswith(("!", "%"))]
    return {"tokens": hashlib.sha256(repr(toks).encode()).hexdigest(),
            "ast": hashlib.sha256(ast.dump(tree).encode()).hexdigest(),
            "magics": magics, "docstrings": docstrings}


def notebook_fingerprint(path):
    nb = json.loads(open(lp(path), "rb").read().decode("utf-8"))
    cells = []
    for c in nb["cells"]:
        src = "".join(c["source"])
        entry = {"type": c["cell_type"],
                 "execution_count": c.get("execution_count"),
                 "outputs": hashlib.sha256(json.dumps(c.get("outputs", []), sort_keys=True).encode()).hexdigest(),
                 "metadata": hashlib.sha256(json.dumps(c.get("metadata", {}), sort_keys=True).encode()).hexdigest()}
        if c["cell_type"] == "code":
            entry.update(code_fingerprint(src))
            entry["n_comments"] = sum(1 for t in tokenize.generate_tokens(io.StringIO(mask(src)).readline)
                                      if t.type == tokenize.COMMENT and not t.string.startswith("#MAGIC"))
        else:
            entry["images"] = hashlib.sha256("".join(re.findall(r"\(data:image/[^)]+\)", src)).encode()).hexdigest()
            entry["n_lines"] = src.count("\n") + 1
        cells.append(entry)
    return {"nbformat": [nb["nbformat"], nb["nbformat_minor"]],
            "metadata": hashlib.sha256(json.dumps(nb["metadata"], sort_keys=True).encode()).hexdigest(),
            "cells": cells}


def data_profile(folder):
    prof = {}
    for f in DATA_FILES:
        p = Path(folder) / f
        entry = {"sha256": sha256(p), "bytes": Path(lp(p)).stat().st_size}
        if f.endswith(".csv"):
            df = pd.read_csv(lp(p), sep=";", encoding="utf-8")
            entry.update(rows=len(df), columns=list(df.columns), dtypes=[str(t) for t in df.dtypes])
        else:
            sheets = pd.read_excel(lp(p), sheet_name=None)
            entry["sheets"] = {k: {"rows": len(v), "columns": [str(c) for c in v.columns]} for k, v in sheets.items()}
        prof[f] = entry
    return prof


def compare_notebooks(ref, cur):
    problems = []
    if ref["nbformat"] != cur["nbformat"] or ref["metadata"] != cur["metadata"]:
        problems.append("notebook-level metadata/format changed")
    if len(ref["cells"]) != len(cur["cells"]):
        return problems + ["cell count %d -> %d" % (len(ref["cells"]), len(cur["cells"]))]
    for i, (a, b) in enumerate(zip(ref["cells"], cur["cells"])):
        for k in ("type", "execution_count", "outputs", "metadata", "tokens", "ast", "magics", "images", "n_comments"):
            if a.get(k) != b.get(k):
                problems.append("cell %d: %s differs" % (i, k))
        if [d[0] for d in a.get("docstrings", [])] != [d[0] for d in b.get("docstrings", [])]:
            problems.append("cell %d: docstring owners differ" % i)
    return problems


def docstring_changes(ref, cur):
    """Documentation-only changes (translated docstrings), reported for review."""
    out = []
    for i, (a, b) in enumerate(zip(ref["cells"], cur["cells"])):
        for (name, old), (_, new) in zip(a.get("docstrings", []), b.get("docstrings", [])):
            if old != new:
                out.append((i, name, " ".join(old.split()), " ".join(new.split())))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--original")
    ap.add_argument("--write-reference")
    a = ap.parse_args()
    if a.write_reference:
        src = Path(a.write_reference)
        REF.write_text(json.dumps({"notebook": notebook_fingerprint(src / "AI Comfort.ipynb"),
                                   "notebook_sha256": sha256(src / "AI Comfort.ipynb"),
                                   "data": data_profile(src / "database")}, indent=1, ensure_ascii=False),
                       encoding="utf-8")
        print("reference written from", src)
        return True
    ref = json.loads(REF.read_text(encoding="utf-8"))
    cur_nb, cur_data = notebook_fingerprint(NOTEBOOK), data_profile(DATA)
    ok = True

    a_problems = compare_notebooks(ref["notebook"], cur_nb)
    n_code = sum(c["type"] == "code" for c in cur_nb["cells"])
    print("Test A - code integrity: %d cells (%d code), %d comments; executable tokens, AST, magics, outputs, "
          "execution counts and metadata compared -> %s" % (len(cur_nb["cells"]), n_code,
          sum(c.get("n_comments", 0) for c in cur_nb["cells"]), "PASS" if not a_problems else "FAIL"))
    for p in a_problems:
        print("   ", p)
    ok &= not a_problems
    docs = docstring_changes(ref["notebook"], cur_nb)
    print("  Documentation-only changes: %d translated docstrings (not executed by the notebook; "
          "no use of __doc__/help/inspect)" % len(docs))
    for i, name, old, new in docs:
        print("    cell %d %s(): %r -> %r" % (i, name, old[:60], new[:60]))

    b_problems = []
    for f, r in ref["data"].items():
        c = cur_data.get(f)
        if c != r:
            b_problems.append("%s: %s" % (f, [k for k in r if r.get(k) != (c or {}).get(k)]))
    extra = sorted(p.name for p in DATA.iterdir() if p.name not in ref["data"] and p.name != "SHA256SUMS")
    if extra:
        b_problems.append("unexpected files in data/: %s" % extra)
    print("Test B - data integrity: %d files; SHA-256, rows, columns, names, dtypes -> %s"
          % (len(cur_data), "PASS" if not b_problems else "FAIL"))
    for p in b_problems:
        print("   ", p)
    ok &= not b_problems

    if a.original:
        src = Path(a.original)
        direct = compare_notebooks(notebook_fingerprint(src / "AI Comfort.ipynb"), cur_nb)
        same_data = all(sha256(src / "database" / f) == sha256(DATA / f) for f in DATA_FILES)
        same_src = sha256(src / "AI Comfort.ipynb") == ref["notebook_sha256"]
        print("Direct comparison with originals: notebook %s; data byte-identical: %s; original notebook "
              "unchanged since reference: %s" % ("PASS" if not direct else direct[:5], same_data, same_src))
        ok &= not direct and same_data and same_src
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if main() else 1)
