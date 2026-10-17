# Publication audit (intellectual property, confidentiality, security)

Audit date: 2026-10-17. Scope: everything in the original folder `Code & Data/`
(1 notebook, 7 data files) and the prepared repository.

**Status (2026-10-17):** the author confirmed holding **written authorisation from Stellantis** to
publish the data and chose the full release (option A below) and the MIT licence for the code. The
authorisation document itself was not reviewed in this audit. The repository was created as
**private** for validation; making it public and archiving it on Zenodo remain separate steps.
No reuse licence has been granted for the data.

## 1. Findings that require a decision by the author

| # | Finding | Evidence | Risk |
|---|---|---|---|
| 1 | The data files are classified **"C2 - Internal"** by a corporate Microsoft Purview (MSIP) sensitivity label | `docProps/custom.xml` of `db_obj.xlsx`, `db_sub.xlsx`, `db_validation.xlsx`: `MSIP_Label_…_Name = "C2 - Internal"`, tenant `d852d5cd-724c-4128-8812-ffa5db3f8507` (the same tenant as the label on the manuscript, which names Stellantis). `db_sub.xlsx` was created by the account "LEONARDO SARZEDAS DO CARMO VIEIRA (EXTERNAL)". The CSV files have no metadata, but they were exported from the same workbooks | Publishing internally classified company data without authorisation |
| 2 | The manuscript states that the subjective data were "derived from an existing database provided by Stellantis"; the notebook title is "SAE Comfort Prediction for Stellantis LATAM \| SimCenter PUC MG" | Manuscript section 3.8; notebook cell 0 | Data ownership lies with a third party (Stellantis) |
| 3 | `db_validation.csv` links measured ride-dynamics metrics to **brand** (Citroën, FIAT, Jeep, Peugeot), **segment** and **body category** of 27 production vehicle models | File content | Model codes are pseudonymised, but brand + segment + category narrows each row to very few commercial vehicles, so the performance data are commercially attributable |
| 4 | Notebook section 4 trains KNN classifiers to **infer the brand and category** of the pseudonymised training vehicles, and the stored outputs display the inferred labels | Cells 23–53 and their outputs | Partial re-identification of the anonymised training set |
| 5 | The stored notebook outputs reproduce the data (table previews, descriptive statistics, 211 static figures and 11 interactive Plotly charts) | Outputs of cells 6–14, 17, 18, 56 onwards | Publishing the notebook with outputs publishes the data even if `data/` is excluded |
| 6 | `db_obj.xlsx` contains **30 additional vehicle runs** (`M026` onwards, Peugeot/FIAT, …) that are absent from `db_obj.csv`, are not used by the notebook and are not reported in the manuscript; `db_sub.xlsx` has 50 additional rows (`Sequency` 32–81) without ratings and a second sheet (`Planilha2`) with a partial copy of the ratings | Row counts: xlsx 62 vs csv 32 | Unintended disclosure of unpublished company data |

## 2. Findings that were checked and are clear

| Check | Result |
|---|---|
| Credentials, tokens, API keys, passwords (source and outputs) | None found |
| Personal data of the test drivers | None: ratings are not linked to people; no names, IDs or physiological data |
| VINs, prototype numbers, internal part numbers | None found (`Model` codes `Mxxx` are pseudonyms) |
| Corporate server names, network paths | None. The only path is the author's personal Google Drive path in cell 3 (`drive/MyDrive/1. Pós-Graduação/…`), which reveals the author's study programme |
| E-mail addresses | None |
| Third-party code embedded in the notebook | None. Only imports of open-source libraries (BSD/MIT/Apache-2.0), which are not redistributed |
| File sizes | Notebook 18.5 MB (outputs, 2 embedded markdown images); data < 40 kB. Below GitHub's 50 MB warning and 100 MB limit; Git LFS not needed |
| Colab metadata | `authorship_tag` (an opaque Colab identifier) is kept unchanged as part of the original file |

## 3. Proposed publication scope (requires the author's choice)

| Option | Public content | Prerequisite |
|---|---|---|
| **A. Full release** | Notebook with outputs, `db_obj.csv`, `db_sub.csv`, `db_validation.csv`, `Dicionário.xlsx` | Written authorisation from Stellantis (data owner) and from PUC Minas/SimCenter if applicable |
| **B. Code-only release** | Notebook **with outputs cleared** (a documented, separate operation — the code itself unchanged), documentation, tests, `CITATION.cff`; data described in `docs/DATA_DICTIONARY.md` but not distributed ("available from Stellantis upon reasonable request and with its permission") | Confirmation that the code and the column names may be disclosed. Results would no longer be reproducible from the repository alone |
| **C. Embargo** | Private repository only; Zenodo deposit with restricted access | No public data access |

The `.xlsx` versions of the data are excluded from the repository under every option (finding 6):
they are not used by the code, and the CSV files contain all the data used in the analysis.
This is a scoping choice, not a modification of the dataset; the original files stay in
`Code & Data/`.

Decision: option A (full release). The private repository contains the notebook with its
outputs, the three CSV files and the dictionary.

## 4. Licensing (to be decided)

Code and data must be licensed separately, and only by the rights holders:

- Notebook code and test scripts: **MIT** (chosen by the author; `LICENSE`).
- Dataset and dictionary: owned by Stellantis according to the manuscript; published with the
  owner's written authorisation (as confirmed by the author). A reuse licence such as CC BY 4.0 can
  only be applied by, or with the permission of, the owner; none is declared.
- Embedded markdown images (`Normalização.png`, cells 223 and 256): author's own diagrams (to be confirmed).
