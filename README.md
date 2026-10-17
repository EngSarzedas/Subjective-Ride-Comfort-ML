# Subjective-Ride-Comfort-ML

Research code and data supporting the study *Machine Learning Techniques for Subjective Ride
Comfort Performance Prediction in Automotive Suspensions*. The repository contains the Jupyter
notebook used for the analysis, the input data, the data dictionary and scripts that verify the
integrity and reproducibility of the published material.

> **Status.** The code is released under the MIT licence. The data are published with the written
> authorisation of their owner, without a reuse licence (see [License and data availability](#license-and-data-availability)).
> The Zenodo archive has not been created yet.

## Project overview

Subjective ride-comfort ratings are expensive to obtain: each one requires a professional test
driver and a physical or simulator run. The study investigates whether machine-learning models can
predict those ratings from objective vehicle-dynamics metrics obtained from virtual vehicle models
and run on a 9-degree-of-freedom driving simulator. With only 32 runs available, it compares
regression and classification formulations, multi-output and single-output strategies, and
reduced feature sets.

## Associated publication

Vieira, L. S. C. *Machine Learning Techniques for Subjective Ride Comfort Performance Prediction in
Automotive Suspensions.* Manuscript in preparation for journal submission (not yet submitted,
peer-reviewed or published). Author affiliation: Department of Mechanical Engineering, Federal
University of Minas Gerais (UFMG), Brazil. ORCID [0009-0001-0776-5159](https://orcid.org/0009-0001-0776-5159).

The manuscript also introduces the *Sarzedas Heuristic* for sample-size estimation. That heuristic
is **not** implemented in this repository (see [Limitations](#limitations)).

## Research methodology

Everything below is implemented in `notebooks/AI Comfort.ipynb` (section numbers refer to the notebook).

1. **Data loading and cleaning (sections 1–3).** Objective metrics (`db_obj.csv`) and subjective
   ratings (`db_sub.csv`) are joined on `Sequency`. Columns with missing values are dropped,
   leaving 28 objective inputs and 7 subjective targets, renamed to the letters `a`–`ak`
   listed in the dictionary.
2. **Brand/category inference (section 4).** PCA, t-SNE and UMAP projections of
   `db_validation.csv`, which has brand and category for each vehicle model. k-nearest-neighbour
   classifiers fitted on that table then predict brand and category for the 32 training runs
   (cell 53). The predicted labels are used to colour and mark the exploratory plots and are
   removed before modelling (cells 217 and 244).
3. **Exploratory data analysis (sections 5–6).** Descriptive statistics, rating distributions,
   Pearson correlation between objective and subjective variables with a ±0.35 threshold, and
   2D/3D scatter plots of the strongest relationships.
4. **Regression (sections 7–9).** The identifiers and the brand/category dummies are dropped,
   so the models use the 28 objective metrics. There are 19 regressors (dummy baseline, linear,
   Lasso, ElasticNet, Bayesian ridge, SGD, k-NN, SVR, linear SVR, decision tree, random forest, extra trees, gradient boosting, AdaBoost, XGBoost, LightGBM, CatBoost, MLP,
   Gaussian process) in scikit-learn pipelines. Tree models are unscaled; the others use
   `RobustScaler`. Multi-output models are native or wrapped with `MultiOutputRegressor`.
   Evaluation uses `cross_val_predict` with 5-fold shuffled `KFold` (`random_state=42`); metrics
   are R², MAE and RMSE. Feature relevance comes from permutation importance and PCA. A re-evaluation
   covers single-output with all features, single-output with the top 3 features
   (`SelectFromModel` inside the pipeline) and multi-output with the top 3 features.
5. **Classification (sections 10–12).** Objective metrics are discretised into quartiles and
   one-hot encoded. Ratings are mapped to three classes: `Regular` < 7.0, `Bom` 7.0–7.5,
   `Ótimo` > 7.5. The same model families are used as classifiers with `StandardScaler`, and
   metrics are accuracy, precision, recall and F1, plus confusion matrices. The same three
   re-evaluation scenarios are repeated (`StratifiedKFold` for single-output).
6. **Final results (section 13).** One summary table across the eight scenario/formulation combinations.

Implementation details and differences from the manuscript are listed in
[`docs/METHODOLOGY_NOTES.md`](docs/METHODOLOGY_NOTES.md).

## Repository structure

```
Subjective-Ride-Comfort-ML/
├── notebooks/AI Comfort.ipynb   analysis notebook (original code and outputs; comments in English)
├── data/
│   ├── db_obj.csv               objective metrics, 32 runs × 39 columns
│   ├── db_sub.csv               subjective ratings, 32 runs × 8 columns
│   ├── db_validation.csv        objective metrics of 27 further vehicle models × 38 columns
│   ├── Dicionário.xlsx          original letter ↔ variable-name dictionary
│   └── SHA256SUMS               checksums of the data files
├── docs/
│   ├── DATA_DICTIONARY.md       variable-level documentation in English
│   ├── METHODOLOGY_NOTES.md     implementation notes and code/manuscript differences
│   ├── REPRODUCIBILITY.md       environment and re-execution results
│   ├── TRANSLATION.md           what was translated and how it was verified
│   ├── PUBLICATION_AUDIT.md     confidentiality / rights audit
│   └── ZENODO_RELEASE.md        release and archiving procedure
├── tests/                       verification scripts (see below)
├── requirements.txt
├── CITATION.cff
└── LICENSE                      MIT licence (code and documentation; not the data)
```

## Dataset description

- **Origin (as stated in the manuscript):** an existing database provided by Stellantis, from
  standard vehicle-dynamics validation protocols. Objective metrics come from virtual subsystem
  models (AdamsCar) run on the 9-DOF driving simulator. Subjective ratings (SAE scale, 0–10) were
  given by a professional test driver.
- **Size:** 32 runs (26 pseudonymised vehicle-model codes) with 34 objective metrics (28 without
  missing values) and 7 ratings; a separate table of 27 vehicle models with brand, segment and category.
- **Missing values:** 283 cells in `db_obj.csv`, 0 in `db_sub.csv`, 382 in `db_validation.csv`.
  The notebook drops the affected columns.
- **Units:** not documented in the original dictionary. Clarification has been requested.

Full variable tables: [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Installation

The analysis was run on Google Colab (Python 3.12). Library versions recorded in the Colab log
are pinned in `requirements.txt`. The versions of scikit-learn, XGBoost, seaborn and umap-learn
were not recorded. A local environment:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install nbclient ipykernel        # only needed to run tests/run_notebook.py
```

The verification run in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) used Python 3.10.11
on Windows 11. With that Python version, scipy 1.15.3 was used, because 1.16.3 requires Python ≥ 3.11.

## Reproducing the results

**Option 1 — Google Colab (original environment).** Upload the three CSV files to
`MyDrive/1. Pós-Graduação/05 - Doutorado Direto/PPGMEC 04 - Dinâmica Veicular Avançada/Artigo/database/`
in your Google Drive (the path read in cell 3), open the notebook in Colab and run all cells in order.

**Option 2 — locally, without editing the notebook.**

```bash
python tests/run_notebook.py --keep tests/_run
```

The script provides a stand-in for `google.colab`, places the CSV files at the relative path the
notebook expects (in a temporary folder), executes every cell in order, and compares the new text
outputs and table contents with the outputs stored in the notebook. The executed notebook is written to
`tests/_run/AI Comfort.executed.ipynb`.

Expected outputs: data previews, correlation tables, the figures, and the regression and
classification result tables of sections 9, 12 and 13.

**Verifying the published material.**

```bash
python tests/check_integrity.py      # Tests A+B: code unchanged except comments/docstrings; data checksums
python tests/check_environment.py    # Test C: every imported module declared and importable
python tests/check_repository.py     # Tests E+F: hygiene, secrets, paths, sizes, README commands
```

## Citation

Please cite the software using [`CITATION.cff`](CITATION.cff); GitHub displays it under
"Cite this repository". Once the first release is archived on Zenodo, the DOI of that version will
be added here. Use the version DOI to refer to the exact material behind the article.

## License and data availability

- **Code** (the notebook code and the scripts in `tests/`) and documentation: [MIT licence](LICENSE).
- **Data** (`data/`): owned by Stellantis according to the manuscript and published with the
  owner's written authorisation, as confirmed by the author. **No reuse licence has been granted
  for the data**, and the MIT licence does **not** apply to them. For any use beyond reading and
  reproducing the published analysis, contact the author. See
  [`docs/PUBLICATION_AUDIT.md`](docs/PUBLICATION_AUDIT.md).

## Limitations

- **Sample size.** n = 32 runs; 6 vehicle models appear twice, and folds are split by run, not by model.
- **Sarzedas Heuristic.** The heuristic and the sample-size, engineering-hour and ROI figures
  reported in the manuscript are not computed in this notebook.
- **Validation scheme.** The notebook uses single 5-fold cross-validation, while the manuscript
  describes repeated k-fold (see `docs/METHODOLOGY_NOTES.md`).
- **Environment.** Several library versions of the original Colab session were not recorded. In
  the verification run, all results were reproduced except the Gaussian Process regression R² in
  two cells of the final table (−7.6451 → −7.6450; −7.5297 → −7.5334) and the LightGBM/k-NN rows of
  the PCA-based variants (see `docs/REPRODUCIBILITY.md`).
- **Language of strings.** Some plot titles, `print` messages and class labels remain in Portuguese
  because they are executable strings (see `docs/TRANSLATION.md`).
- **Data documentation.** Units and measurement definitions are not documented in the original
  data dictionary.
