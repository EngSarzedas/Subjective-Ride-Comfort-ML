"""Test D - execute the published notebook unchanged and compare with its stored (original) outputs.

The notebook was written for Google Colab. Without editing it, this harness:
  * provides a stub `google.colab` module (drive.mount / files are no-ops);
  * recreates the relative Google Drive path read by cell 3 inside a temporary working directory
    and places the published CSV files there;
  * runs every cell in order with nbclient, then compares the text outputs and the contents of
    HTML tables cell by cell: identical text, or identical numbers at the displayed precision.
Figures (PNG) and Plotly charts are not compared (rendering-dependent); table styling is ignored.

  python tests/run_notebook.py [--timeout 3600] [--keep DIR]
  python tests/run_notebook.py --compare DIR/AI Comfort.executed.ipynb   (re-compare a saved run)
Requires the packages in requirements.txt plus nbclient and ipykernel.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "AI Comfort.ipynb"
DRIVE_DIR = ("drive/MyDrive/1. Pós-Graduação/05 - Doutorado Direto/"
             "PPGMEC 04 - Dinâmica Veicular Avançada/Artigo/database")
NUM = re.compile(r"-?\d+\.\d+(?:e[+-]?\d+)?|-?\d+")
VOLATILE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|"
                      r"\d+(\.\d+)?\s*(s|sec|seconds|ms)\b|<[^>]+ at 0x[0-9a-f]+>|0x[0-9a-f]+")

STUB = '''"""Local stand-in for google.colab used only by tests/run_notebook.py."""
class _Drive:
    @staticmethod
    def mount(path, *args, **kwargs):
        print("Mounted at " + path)
class _Files:
    @staticmethod
    def download(path):
        print("download skipped: " + str(path))
drive = _Drive()
files = _Files()
'''


def lp(p):
    s = str(Path(p).resolve())
    return "\\\\?\\" + s if sys.platform == "win32" and not s.startswith("\\\\?\\") else s


def html_table_text(html):
    """Cell contents of HTML tables (pandas DataFrame/Styler output), one table row per line.
    Styling, random Styler ids and Plotly scripts are ignored."""
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", re.sub(r"(?s)<style.*?</style>|<script.*?</script>", "", html), re.S):
        cells = [re.sub(r"<[^>]+>|&nbsp;", " ", c).strip()
                 for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        rows.append("\t".join(cells))
    return "\n".join(rows)


def text_outputs(cell):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            out.append("".join(o.get("text", [])))
        elif o.get("output_type") in ("execute_result", "display_data"):
            data = o.get("data", {})
            if "text/html" in data and "<table" in "".join(data["text/html"]):
                out.append(html_table_text("".join(data["text/html"])))
            elif "text/plain" in data and "image/png" not in data:
                out.append("".join(data["text/plain"]))
        elif o.get("output_type") == "error":
            out.append("ERROR %s: %s" % (o.get("ename"), o.get("evalue")))
    return "\n".join(out)


HIDDEN = "Output hidden; open in https://colab.research.google.com to view."


def normalise(t):
    """Drop volatile tokens and blank lines (stderr/stdout interleaving differs between runs)."""
    lines = VOLATILE.sub("<v>", t).splitlines()
    return "\n".join(l.rstrip() for l in lines if l.strip())


def numbers(t):
    return NUM.findall(normalise(t))


def same_numbers(a, b):
    """Numbers equal when rounded to the precision shown in the original output."""
    na, nb = numbers(a), numbers(b)
    if len(na) != len(nb):
        return False
    for x, y in zip(na, nb):
        dec = len(x.split(".")[1]) if "." in x and "e" not in x.lower() else 0
        try:
            fx, fy = float(x), float(y)
        except ValueError:
            return False
        # equal at the displayed precision, or within floating-point round-off (full-precision reprs)
        if round(fx, dec) != round(fy, dec) and abs(fx - fy) > 1e-12 * max(1.0, abs(fx)):
            return False
    return True


def differing_lines(a, b, limit=6):
    la, lb = normalise(a).splitlines(), normalise(b).splitlines()
    return [(x, y) for x, y in zip(la, lb) if x != y and not same_numbers(x, y)][:limit] or \
        [("<%d lines>" % len(la), "<%d lines>" % len(lb))]


def compare(original_cells, executed_cells):
    counts = dict.fromkeys(["identical", "numerically equal", "different", "error", "no text output",
                            "no reference (output hidden in original)", "environment log (pip/apt)"], 0)
    rows = []
    for i, (c0, c1) in enumerate(zip(original_cells, executed_cells)):
        if c0["cell_type"] != "code":
            continue
        t0_, t1_ = text_outputs(c0), text_outputs(c1)
        if any(o.get("output_type") == "error" for o in c1.get("outputs", [])):
            status = "error"
        elif t0_.strip() == HIDDEN:
            status = "no reference (output hidden in original)"
        elif "".join(c0["source"]).lstrip().startswith("!pip"):
            status = "environment log (pip/apt)"
        elif not t0_.strip() and not t1_.strip():
            status = "no text output"
        elif normalise(t0_) == normalise(t1_):
            status = "identical"
        elif same_numbers(t0_, t1_):
            status = "numerically equal"
        else:
            status = "different"
        counts[status] += 1
        if status in ("different", "error"):
            rows.append((i, status, differing_lines(t0_, t1_)))
    return counts, rows


def report(counts, rows, elapsed=None):
    if elapsed is not None:
        print("Executed %d code cells in %.0f s" % (sum(counts.values()), elapsed))
    for k, v in counts.items():
        print("  %-42s %d" % (k, v))
    for i, s, lines in rows:
        print("  cell %d [%s]" % (i, s))
        for x, y in lines:
            print("    original: %s\n    rerun:    %s" % (x[:160], y[:160]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--keep")
    ap.add_argument("--compare", help="compare an already executed notebook instead of running")
    a = ap.parse_args()
    original = json.loads(open(lp(NOTEBOOK), "rb").read().decode("utf-8"))
    if a.compare:
        executed = json.loads(open(lp(a.compare), "rb").read().decode("utf-8"))
        counts, rows = compare(original["cells"], executed["cells"])
        report(counts, rows)
        return counts["error"] == 0 and counts["different"] == 0

    import nbformat
    from nbclient import NotebookClient
    work = Path(tempfile.mkdtemp(prefix="nbrun_"))
    shim = work / "_shim" / "google" / "colab"
    shim.mkdir(parents=True)
    (shim / "__init__.py").write_text(STUB, encoding="utf-8")
    data_dir = work / DRIVE_DIR
    data_dir.mkdir(parents=True)
    for f in ("db_obj.csv", "db_sub.csv", "db_validation.csv"):
        shutil.copyfile(lp(ROOT / "data" / f), lp(data_dir / f))

    env_path = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get("PATH", "")])
    os.environ["PATH"] = env_path                                # '!pip' resolves to this environment
    os.environ["PYTHONPATH"] = os.pathsep.join([str(work / "_shim"), os.environ.get("PYTHONPATH", "")])
    nb = nbformat.reads(json.dumps(original), as_version=4)
    client = NotebookClient(nb, timeout=a.timeout, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(work)}})
    t0 = time.time()
    client.execute()
    elapsed = time.time() - t0

    counts, rows = compare(original["cells"], json.loads(nbformat.writes(nb))["cells"])
    report(counts, rows, elapsed)
    if a.keep:
        Path(a.keep).mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, lp(Path(a.keep) / "AI Comfort.executed.ipynb"))
        Path(lp(Path(a.keep) / "comparison.json")).write_text(
            json.dumps({"counts": counts, "elapsed_s": elapsed, "differences": rows}, indent=1, ensure_ascii=False),
            encoding="utf-8")
    shutil.rmtree(lp(work), ignore_errors=True)
    return counts["error"] == 0 and counts["different"] == 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if main() else 1)
