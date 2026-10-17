# Translation of the notebook comments

The original notebook was written with comments and explanatory markdown in Brazilian Portuguese.
In the published copy these were translated into English. Nothing executable was changed.

| Item | Translated | Kept in Portuguese |
|---|---|---|
| Code comments (`# ...`) | 638 occurrences (486 distinct texts) out of 798 comments | Class labels quoted inside comments (`'Regular'`, `'Bom'`, `'Ótimo'`), because they are values used by the code |
| Markdown cells | 62 lines in 22 cells | Image alt text `Normalização.png`; text inside the two embedded images (cells 223 and 256) |
| String literals (`print` messages, plot titles and axis labels, dictionary keys, file paths) | none | All, because they are executed and appear in outputs |
| Docstrings of functions/classes | 16 (cells 237–276); the notebook never reads `__doc__` (no `help`, `inspect` or `?`), so they do not affect execution | — (the one in cell 18 was already in English) |
| Stored outputs | none | All, because they are the original results |

Method: comments were located with Python's `tokenize` module (IPython `!`/`%` lines treated as
opaque) and replaced in place by exact text match; markdown lines were replaced by exact line
match; the notebook JSON was re-serialised in its original compact format, so that the file
differs from the original only in the translated text.

Verification (`python tests/check_integrity.py --original "<folder>"`): for each of the 212 code
cells, the token stream and the abstract syntax tree, both without comments and docstrings, are
identical to the original; the 16 translated docstrings are listed separately as
documentation-only changes; outputs, execution counts and cell/notebook metadata are
byte-for-byte unchanged. The check fails when an executable token or string is altered (tested
with `random_state`, `n_splits`, a correlation threshold, a `print` message, a plot label and a
function name).

Typos in the original English comments (for example `GussianProcessRegressor`, `seat reail`) were
left as they are.
