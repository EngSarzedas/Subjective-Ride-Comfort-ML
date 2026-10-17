"""Test C - dependencies. Every module imported by the notebook must be declared in
requirements.txt (or be part of the standard library / Colab runtime) and importable here.
  python tests/check_environment.py
"""
import ast
import importlib
import importlib.metadata as md
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_integrity import NOTEBOOK, lp, mask  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DIST = {"sklearn": "scikit-learn", "umap": "umap-learn", "dataframe_image": "dataframe-image",
        "IPython": "ipython", "mpl_toolkits": "matplotlib"}
COLAB_ONLY = {"google"}            # google.colab: provided by Colab; replaced by a stub in tests/run_notebook.py


def notebook_imports():
    nb = json.loads(open(lp(NOTEBOOK), "rb").read().decode("utf-8"))
    mods = set()
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            for n in ast.walk(ast.parse(mask("".join(c["source"])))):
                if isinstance(n, ast.Import):
                    mods |= {a.name.split(".")[0] for a in n.names}
                elif isinstance(n, ast.ImportFrom) and n.module:
                    mods.add(n.module.split(".")[0])
    return mods


def declared():
    names = set()
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line.split("#")[0])
        if m:
            names.add(m.group(1).lower())
    return names


def main():
    mods = notebook_imports()
    req = declared()
    stdlib = set(sys.stdlib_module_names)
    rows, ok = [], True
    for m in sorted(mods):
        if m in stdlib:
            rows.append((m, "standard library", "-", "OK"))
            continue
        if m in COLAB_ONLY:
            rows.append((m, "Google Colab runtime", "stub in tests/run_notebook.py", "OK"))
            continue
        dist = DIST.get(m, m)
        listed = dist.lower() in req
        try:
            importlib.import_module(m)
            ver = md.version(dist)
        except Exception as e:                       # noqa: BLE001
            ver = "NOT IMPORTABLE (%s)" % type(e).__name__
        good = listed and not ver.startswith("NOT")
        ok &= good
        rows.append((m, dist + ("" if listed else " (NOT in requirements.txt)"), ver, "OK" if good else "FAIL"))
    print("Test C - Python %s" % sys.version.split()[0])
    for r in rows:
        print("  %-16s %-34s %-28s %s" % r)
    unused = sorted(req - {DIST.get(m, m).lower() for m in mods} - {"ipython", "scipy", "nest-asyncio"})
    print("  Declared but not imported directly: %s" % (unused or "none"))
    print("RESULT:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
