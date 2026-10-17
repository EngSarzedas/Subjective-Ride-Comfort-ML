# Data dictionary

This document describes the files in `data/`. Its primary reference is the author's original
dictionary, `data/Dicionário.xlsx`, which is preserved unchanged. Every number below was computed
from the published files (`python tests/check_integrity.py` re-checks checksums, shapes, headers
and dtypes).

## What the original dictionary contains

`Dicionário.xlsx` (sheet `Planilha2`) maps the short letters used in the notebook to the original
column headers:

- columns `Letter` / `Original Name`: the 37 columns of the merged training table
  (`db_obj.csv` + `db_sub.csv`, after the notebook drops columns with missing values), letters `a`–`ak`;
- columns `Letter.1` / `Original Name.1`: the 20 columns of the validation table
  (`db_validation.csv`, after the same step), letters `a`–`t`.

Both mappings were verified against the notebook's renaming logic (37/37 and 20/20 matches).
The letters are **not** the same across the two tables (for example, `c` is a seat-rail
acceleration in the training table and `Category` in the validation table).

The original dictionary does **not** give definitions, units, measurement procedures or valid
ranges. Those fields are therefore marked as *not documented* below; they need to be supplied by
the author before the dataset can be interpreted without the manuscript.

## Files

| File | Rows | Columns | Content | Used by the notebook |
|---|---|---|---|---|
| `db_obj.csv` | 32 | 39 | Objective metrics per simulator run | Yes (cell 3) |
| `db_sub.csv` | 32 | 8 | Subjective ratings per simulator run | Yes (cell 3) |
| `db_validation.csv` | 27 | 38 | Objective metrics of a second set of vehicle models, with segment, category and brand | Yes (cell 3) |
| `Dicionário.xlsx` | 37 | 4 | Letter ↔ original-header mapping | No (reference only) |
| `SHA256SUMS` | — | — | SHA-256 checksums of the four files above | Tests |

Format of the CSV files: UTF-8 with byte-order mark, `;` as field separator, `.` as decimal
separator, CRLF line endings. Read them exactly as the notebook does:
`pd.read_csv(path, encoding="utf-8", on_bad_lines="skip", sep=";")`.

Headers are kept verbatim. Several contain non-breaking spaces (U+00A0), zero-width spaces
(U+200B), en dashes, a double space and the original spelling `Foce` (column 32 of `db_obj.csv`);
they must not be "cleaned", because the notebook and the dictionary rely on the exact strings.

## Relationships

- `db_obj.csv` and `db_sub.csv` are joined on `Sequency` (0–31, one row per simulator run).
  `Model` is a pseudonymised vehicle-model code; 6 models (`M002`, `M003`, `M006`, `M008`,
  `M011`, `M023`) appear in two runs each, so the 32 runs cover 26 model codes.
- `db_validation.csv` has 27 rows (`M000`, `M056`–`M081`). Only `M000` also appears in the training
  table. The notebook uses this table only in section 4, where KNN classifiers predict `Category`
  and `Brand` (see `docs/METHODOLOGY_NOTES.md`).

## Roles

- **Target**: the 7 subjective ratings in `db_sub.csv` (letters `ae`–`ak`). According to the
  manuscript they are SAE-scale (0–10) ratings given by a professional test driver; the observed
  range is 6.00–8.25.
- **Input**: the objective metrics that remain after the notebook drops columns with missing values
  (letters `c`–`ad`, 28 variables).
- **Identifier**: `Model`, `Sequency`.
- **Categorical descriptor**: `Segment`, `Category`, `Brand`.
- Columns flagged "dropped by the notebook" exist in the files but are removed by cell 15 because
  they contain missing values; they do not enter any model.

## Missing values

| File | Missing cells | Notes |
|---|---|---|
| `db_obj.csv` | 283 | `Segment`, `Category`, `Brand` filled only for `M000`; 4 RMS columns (lateral, floor) empty; the two "Peak to peak" columns hold only a text placeholder in Portuguese (`obter phi max menos o phi minimo` / `obter theta max menos o theta minimo`, i.e. "obtain max phi minus min phi") in the first row |
| `db_sub.csv` | 0 | — |
| `db_validation.csv` | 382 | 3–27 missing values in 18 columns (see table) |

## Undocumented items (clarification requested from the author)

1. Units of every objective metric (accelerations, dissipation times, ratios, forces).
2. Definitions: what "Dissipation Time", "Ratio Front / Rear", "XXG" and "ZZG" denote
   (presumably longitudinal and vertical channels), and how the RMS bands were computed.
3. Meaning of `Segment` codes (`B`, `C`, `C/D`) and `Category` codes (`SUP`, …).
4. What `Sequency` represents (run order, test session?).

## Variables

Units and definitions: **not documented** in the original dictionary for any variable (see above). Min/Max are the observed values in the file.

#### `data/db_obj.csv` — 32 rows × 39 columns

| # | Variable name (header as stored) | Notebook letter | Data type | Non-null | Min | Max | Role | Observed values |
|---|---|---|---|---|---|---|---|---|
| 1 | Model | a | object | 32/32 | — | — | Identifier | `M000`, `M001`, `M002`, `M003`, `M004`, `M005`, `M006`, `M007` … (26 distinct) |
| 2 | Sequency | b | int64 | 32/32 | 0 | 31 | Identifier / join key | 32 distinct |
| 3 | Segment | — (dropped by the notebook: contains missing values) | object | 1/32 | — | — | Categorical descriptor | `C` |
| 4 | Category | — (dropped by the notebook: contains missing values) | object | 1/32 | — | — | Categorical descriptor | `SUV` |
| 5 | Brand | — (dropped by the notebook: contains missing values) | object | 1/32 | — | — | Categorical descriptor | `Citroën` |
| 6 | Front Longitudinal Acceleration Seat Rail – XXG | c | float64 | 32/32 | 0.395 | 0.58 | Input | 22 distinct |
| 7 | Front Longitudinal Dissipation Time Seat Rail – XXG | d | float64 | 32/32 | 0.083 | 0.193 | Input | 9 distinct |
| 8 | Rear Longitudinal Acceleration Seat Rail – XXG | e | float64 | 32/32 | 1.027 | 1.439 | Input | 20 distinct |
| 9 | Rear Longitudinal Dissipation Time Seat Rail - XXG | f | float64 | 32/32 | 0.119 | 0.218 | Input | 15 distinct |
| 10 | Ratio Front / Rear Acc Seat Rail - XXG | g | float64 | 32/32 | 0.289802 | 0.452775 | Input | 25 distinct |
| 11 | Ratio Front / Rear Dissipation Seat Rail - XXG | h | float64 | 32/32 | 0.399083 | 1.62185 | Input | 17 distinct |
| 12 | Front Vertical Acceleration Seat Rail – ZZG | i | float64 | 32/32 | 0.279 | 0.387 | Input | 21 distinct |
| 13 | Front Vertical Dissipation Time Seat Rail – ZZG | j | float64 | 32/32 | 0.076 | 0.178 | Input | 10 distinct |
| 14 | Rear Vertical Acceleration Seat Rail – ZZG | k | float64 | 32/32 | 0.637 | 0.88 | Input | 21 distinct |
| 15 | Rear Vertical Dissipation Time Seat Rail - ZZG | l | float64 | 32/32 | 0.106 | 0.255 | Input | 16 distinct |
| 16 | Ratio Front / Rear Acc Seat Rail - ZZG | m | float64 | 32/32 | 0.36897 | 0.596546 | Input | 25 distinct |
| 17 | Ratio Front / Rear Dissipation Seat Rail - ZZG | n | float64 | 32/32 | 0.408602 | 1.67925 | Input | 21 distinct |
| 18 | RMS longitudinal acceleration at seat rail (0.5 to 3 Hz) | o | float64 | 32/32 | 0.0119 | 0.0132 | Input | 12 distinct |
| 19 | RMS longitudinal acceleration at seat rail (3 to 8 Hz) | p | float64 | 32/32 | 0.0087 | 0.0139 | Input | 14 distinct |
| 20 | RMS longitudinal acceleration at seat rail (8 to 20 Hz) | q | float64 | 32/32 | 0.0495 | 0.0656 | Input | 22 distinct |
| 21 | RMS vertical acceleration at seat rail (0.5 to 3 Hz) | r | float64 | 32/32 | 0.0441 | 0.0599 | Input | 20 distinct |
| 22 | RMS vertical acceleration at seat rail (3 to 8 Hz) | s | float64 | 32/32 | 0.0512 | 0.0629 | Input | 22 distinct |
| 23 | RMS vertical acceleration at seat rail (8 to 20 Hz) | t | float64 | 32/32 | 0.0703 | 0.1056 | Input | 25 distinct |
| 24 | RMS lateral acceleration at seat rail (0.5 to 3 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/32 | — | — | Input | all missing |
| 25 | RMS vertical acceleration at floor (0.5 to 3 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/32 | — | — | Input | all missing |
| 26 | RMS vertical acceleration at floor (3 to 8 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/32 | — | — | Input | all missing |
| 27 | RMS vertical acceleration at floor (8 to 20 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/32 | — | — | Input | all missing |
| 28 | RMS pitch acceleration (0.5 to 3 Hz) | u | float64 | 32/32 | 23.6 | 28.4 | Input | 14 distinct |
| 29 | RMS roll acceleration (0.5 to 3 Hz) | v | float64 | 32/32 | 21.1 | 25.6 | Input | 17 distinct |
| 30 | Peak Jounce Front Left at TopMount Vertical Force – ZZG | w | float64 | 32/32 | 1270.82 | 1768.97 | Input | 26 distinct |
| 31 | Peak Jounce Front Right at TopMount Vertical Force – ZZG | x | float64 | 32/32 | 920.148 | 1502.67 | Input | 26 distinct |
| 32 | Peak Jounce Rear Left at TopMount Vertical Force – ZZG | y | float64 | 32/32 | 1601.28 | 1948.27 | Input | 26 distinct |
| 33 | Peak Jounce Rear Right at TopMount Vertical Foce – ZZG | z | float64 | 32/32 | 1425.39 | 1748.81 | Input | 26 distinct |
| 34 | Peak Rebound Front Left at TopMount Vertical Force – ZZG | aa | float64 | 32/32 | -1465.22 | -1048.13 | Input | 26 distinct |
| 35 | Peak Rebound Front Right at TopMount Vertical Force – ZZG | ab | float64 | 32/32 | -1062.85 | -794.031 | Input | 26 distinct |
| 36 | Peak Rebound Rear Left at hub TopMount Vertical Force – ZZG | ac | float64 | 32/32 | -1213.34 | -877.141 | Input | 25 distinct |
| 37 | Peak Rebound Rear Right at hub TopMount Vertical Force – ZZG | ad | float64 | 32/32 | -818.829 | -655.502 | Input | 26 distinct |
| 38 | Peak to peak pitch amplitude | — (dropped by the notebook: contains missing values) | object | 1/32 | — | — | Input | `obter phi max menos o phi minimo` |
| 39 | Peak to peak roll amplitude | — (dropped by the notebook: contains missing values) | object | 1/32 | — | — | Input | `obter theta max menos o theta minimo` |

#### `data/db_sub.csv` — 32 rows × 8 columns

| # | Variable name (header as stored) | Notebook letter | Data type | Non-null | Min | Max | Role | Observed values |
|---|---|---|---|---|---|---|---|---|
| 1 | Sequency | b (shared with db_obj) | int64 | 32/32 | 0 | 31 | Identifier / join key | 32 distinct |
| 2 | Low frequency vertical comfort (0 to 3 Hz) | ae | float64 | 32/32 | 6.25 | 7.75 | Target | 7 distinct |
| 3 | Smoothness (3 to 8 Hz) | af | float64 | 32/32 | 6.5 | 7.5 | Target | 5 distinct |
| 4 | Wheel Bounce | ag | float64 | 32/32 | 6 | 7.5 | Target | 7 distinct |
| 5 | Vibrations | ah | float64 | 32/32 | 6.25 | 7.5 | Target | 6 distinct |
| 6 | Impact | ai | float64 | 32/32 | 6.25 | 8.25 | Target | 8 distinct |
| 7 | Pitch | aj | float64 | 32/32 | 6.5 | 7.5 | Target | 5 distinct |
| 8 | Roll | ak | float64 | 32/32 | 6.25 | 7.5 | Target | 6 distinct |

#### `data/db_validation.csv` — 27 rows × 38 columns

| # | Variable name (header as stored) | Notebook letter | Data type | Non-null | Min | Max | Role | Observed values |
|---|---|---|---|---|---|---|---|---|
| 1 | Model | a | object | 27/27 | — | — | Identifier | `M000`, `M056`, `M057`, `M058`, `M059`, `M060`, `M061`, `M062` … (27 distinct) |
| 2 | Segment | b | object | 27/27 | — | — | Categorical descriptor | `B`, `C`, `C/D` |
| 3 | Category | c | object | 27/27 | — | — | Categorical descriptor | `Hatch`, `Pickup`, `SUP`, `SUV`, `SUV Crossover` |
| 4 | Brand | d | object | 27/27 | — | — | Categorical descriptor | `Citroën`, `FIAT`, `Jeep`, `Peugeot` |
| 5 | Front Longitudinal Acceleration Seat Rail – XXG | e | float64 | 27/27 | 0.461 | 1.45 | Input | 27 distinct |
| 6 | Front Longitudinal Dissipation Time Seat Rail – XXG | f | float64 | 27/27 | 0.076 | 0.21 | Input | 23 distinct |
| 7 | Rear Longitudinal Acceleration Seat Rail – XXG | g | float64 | 27/27 | 0.61 | 1.961 | Input | 27 distinct |
| 8 | Rear Longitudinal Dissipation Time Seat Rail - XXG | h | float64 | 27/27 | 0.03 | 0.207 | Input | 25 distinct |
| 9 | Ratio Front / Rear Acc Seat Rail - XXG | i | float64 | 27/27 | 0.394558 | 1.545 | Input | 27 distinct |
| 10 | Ratio Front / Rear Dissipation Seat Rail - XXG | j | float64 | 27/27 | 0.561 | 2.692 | Input | 27 distinct |
| 11 | Front Vertical Acceleration Seat Rail – ZZG | k | float64 | 27/27 | 0.313 | 0.909 | Input | 27 distinct |
| 12 | Front Vertical Dissipation Time Seat Rail – ZZG | l | float64 | 27/27 | 0.048 | 0.205 | Input | 20 distinct |
| 13 | Rear Vertical Acceleration Seat Rail – ZZG | m | float64 | 27/27 | 0.538 | 1.099 | Input | 26 distinct |
| 14 | Rear Vertical Dissipation Time Seat Rail - ZZG | n | float64 | 27/27 | 0.068 | 0.207 | Input | 22 distinct |
| 15 | Ratio Front / Rear Acc Seat Rail - ZZG | o | float64 | 27/27 | 0.439607 | 0.993 | Input | 27 distinct |
| 16 | Ratio Front / Rear Dissipation Seat Rail - ZZG | p | float64 | 27/27 | 0.527 | 2.628 | Input | 27 distinct |
| 17 | RMS longitudinal acceleration at seat rail (0.5 to 3 Hz) | q | float64 | 27/27 | 0.007 | 0.018 | Input | 10 distinct |
| 18 | RMS longitudinal acceleration at seat rail (3 to 8 Hz) | — (dropped by the notebook: contains missing values) | float64 | 24/27 | 0.011 | 0.024 | Input | 12 distinct |
| 19 | RMS longitudinal acceleration at seat rail (8 to 20 Hz) | — (dropped by the notebook: contains missing values) | float64 | 24/27 | 0.035 | 0.105 | Input | 20 distinct |
| 20 | RMS vertical acceleration at seat rail (0.5 to 3 Hz) | r | float64 | 27/27 | 0.045 | 0.09 | Input | 17 distinct |
| 21 | RMS vertical acceleration at seat rail (3 to 8 Hz) | — (dropped by the notebook: contains missing values) | float64 | 24/27 | 0.0554 | 0.113 | Input | 19 distinct |
| 22 | RMS vertical acceleration at seat rail (8 to 20 Hz) | — (dropped by the notebook: contains missing values) | float64 | 24/27 | 0.0791 | 0.15 | Input | 22 distinct |
| 23 | RMS lateral acceleration at seat rail (0.5 to 3 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
| 24 | RMS vertical acceleration at floor (0.5 to 3 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
| 25 | RMS vertical acceleration at floor (3 to 8 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
| 26 | RMS vertical acceleration at floor (8 to 20 Hz) | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
| 27 | RMS pitch acceleration (0.5 to 3 Hz) | s | float64 | 27/27 | 24.3 | 48.603 | Input | 26 distinct |
| 28 | RMS roll acceleration (0.5 to 3 Hz) | t | float64 | 27/27 | 14.561 | 27.973 | Input | 27 distinct |
| 29 | Peak Jounce Front Left at TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | 1524.94 | 1524.94 | Input | 1 distinct |
| 30 | Peak Jounce Front Right at TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | 1086.81 | 1086.81 | Input | 1 distinct |
| 31 | Peak Jounce Rear Left at TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | 1789.63 | 1789.63 | Input | 1 distinct |
| 32 | Peak Jounce Rear Right at TopMount Vertical Foce – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | 1588.52 | 1588.52 | Input | 1 distinct |
| 33 | Peak Rebound Front Left at TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | -1255.01 | -1255.01 | Input | 1 distinct |
| 34 | Peak Rebound Front Right at TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | -914.083 | -914.083 | Input | 1 distinct |
| 35 | Peak Rebound Rear Left at hub TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | -1046.96 | -1046.96 | Input | 1 distinct |
| 36 | Peak Rebound Rear Right at hub TopMount Vertical Force – ZZG | — (dropped by the notebook: contains missing values) | float64 | 1/27 | -740.912 | -740.912 | Input | 1 distinct |
| 37 | Peak to peak pitch amplitude | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
| 38 | Peak to peak roll amplitude | — (dropped by the notebook: contains missing values) | float64 | 0/27 | — | — | Input | all missing |
