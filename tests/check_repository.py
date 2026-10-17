"""Tests E and F - repository hygiene and documentation.

E: no credentials or secrets (files, notebook outputs and full Git history); no temporary or
   unwanted files; no local absolute paths in the documentation and scripts; file sizes compatible with
   GitHub; .gitignore effective; tracked files identical to the working tree.
F: every command and path cited in README.md exists, and every script option used in the README
   is accepted by that script.
  python tests/check_repository.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(
    r"(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|AIza[0-9A-Za-z_\-]{35}|sk-[A-Za-z0-9]{32,}|"
    r"(?i:(password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]{6,}['\"]))")
LOCAL_PATH = re.compile(r"[A-Za-z]:\\\\?Users\\\\?|/Users/[a-z]|/home/[a-z]|\\\\Users\\\\", re.I)
UNWANTED = re.compile(r"(\.pyc$|__pycache__|\.ipynb_checkpoints|~\$|\.tmp$|\.bak$|Thumbs\.db|\.DS_Store|\.xlsx$)")
ALLOWED_XLSX = {"data/Dicionário.xlsx"}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def tracked():
    """Files that are (or would be) versioned: tracked plus untracked-but-not-ignored."""
    r = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if r.returncode != 0:
        return None
    return sorted({p for p in r.stdout.split("\0") if p})


def main():
    ok = True
    files = tracked()
    in_git = files is not None
    if not in_git:
        files = [str(p.relative_to(ROOT)).replace("\\", "/") for p in ROOT.rglob("*")
                 if p.is_file() and ".git" not in p.parts and "_run" not in p.parts]
    issues = []
    for f in files:
        p = ROOT / f
        size = p.stat().st_size
        if size > 100 * 1024 ** 2:
            issues.append("over GitHub 100 MB limit: %s" % f)
        elif size > 50 * 1024 ** 2:
            issues.append("over 50 MB (GitHub warning): %s" % f)
        if UNWANTED.search(f) and f not in ALLOWED_XLSX:
            issues.append("unwanted file: %s" % f)
        text = p.read_bytes().decode("utf-8", errors="ignore")
        if SECRET.search(text):
            issues.append("possible secret in %s: %s" % (f, SECRET.search(text).group(0)[:20]))
        if f.endswith((".md", ".py", ".cff", ".txt")) and f != "tests/check_repository.py" and LOCAL_PATH.search(text):
            issues.append("local absolute path in %s" % f)
    has_commits = in_git and git("rev-parse", "--verify", "HEAD").returncode == 0
    if has_commits:
        hist = git("log", "--all", "-p", "--no-color").stdout
        if SECRET.search(hist):
            issues.append("possible secret in Git history")
        status = git("status", "--porcelain").stdout.strip()
        if status:
            issues.append("working tree differs from the last commit:\n" + status)
    if in_git:
        for probe in ("tests/_run/x.ipynb", "data/db_obj.xlsx", "notebooks/.ipynb_checkpoints/a", "__pycache__/a.pyc"):
            if git("check-ignore", "-q", probe).returncode != 0:
                issues.append(".gitignore does not ignore %s" % probe)
    scope = ("versioned files + Git history" if has_commits else
             "files that would be committed; no commit yet, history not checked" if in_git else
             "working tree, Git not initialised")
    print("Test E - hygiene: %d files checked (%s) -> %s" % (len(files), scope, "PASS" if not issues else "FAIL"))
    for i in issues:
        print("   ", i)
    ok &= not issues

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    f_issues = []
    for m in re.finditer(r"python (tests/[\w.]+\.py)([^\n#]*)", readme):
        script, opts = m.group(1), m.group(2)
        if not (ROOT / script).exists():
            f_issues.append("missing script %s" % script)
            continue
        src = (ROOT / script).read_text(encoding="utf-8")
        for opt in re.findall(r"(--[\w-]+)", opts):
            if '"%s"' % opt not in src:
                f_issues.append("%s does not accept %s" % (script, opt))
    for link in re.findall(r"\]\(((?!https?:|#)[^)]+)\)", readme):
        if not (ROOT / link).exists():
            f_issues.append("broken link %s" % link)
    for path in re.findall(r"`((?:notebooks|data|docs|tests)/[^`*]+?)`", readme):
        if "_run" not in path and not (ROOT / path).exists():
            f_issues.append("path not found %s" % path)
    if "requirements.txt" not in files:
        f_issues.append("requirements.txt not present")
    print("Test F - documentation: README commands, options, links and paths -> %s" % ("PASS" if not f_issues else "FAIL"))
    for i in f_issues:
        print("   ", i)
    ok &= not f_issues
    return ok


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if main() else 1)
