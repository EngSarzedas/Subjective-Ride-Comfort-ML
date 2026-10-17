# Methodology notes

Observations made while preparing this repository. **None of them was corrected**: the notebook is
published with its original behaviour, and these notes are for readers and for the author.
Cell numbers are 0-based indices in `notebooks/AI Comfort.ipynb`.

## Differences between the code and the manuscript

1. **Cross-validation.** The manuscript describes "Repeated k-fold Cross-Validation ... k = 5
   folds, repeated five times". The code uses a single `KFold(n_splits=5, shuffle=True,
   random_state=42)` (cells 226, 258, 268) or `StratifiedKFold` with the same settings (cell 268),
   through `cross_val_predict`. `RepeatedKFold` is not used.
2. **Sarzedas Heuristic.** The heuristic (manuscript Eqs. 8–12) and the sample-size estimates
   derived from it (n ≈ 1,434 / 1,730 / 3,460; 4,302–10,380 engineering hours; ROI) are **not
   implemented** in the notebook. This repository therefore does not reproduce those numbers.
3. **Permutation importance.** The comment in cell 231 says `n_repeats=5`; the call uses
   `n_repeats=10` (cells 231 and 264).
4. **Scaling.** The regression pipelines use `RobustScaler` (cells 227, 238–240), except the
   PCA-based variant in cell 233, which uses `StandardScaler`; the classification pipelines use
   `StandardScaler` (cells 259, 266, 271–273), as stated in the markdown cells 223 and 256. The
   manuscript mentions only `RobustScaler`.

## Implementation details worth knowing

- **Feature set.** Cell 15 drops every column that has at least one missing value. Its comment
  says the step should be removed "once all data are complete". It defines the 28 objective
  inputs actually modelled (`c`–`ad`).
- **Classification targets** (cells 250 and 269): each subjective rating becomes three classes,
  `Regular` (< 7.0), `Bom` (7.0–7.5) and `Ótimo` (> 7.5). The labels are Portuguese strings used by
  the code and were therefore not translated.
- **Classification inputs** (cell 246): every objective metric is discretised into quartiles
  (`pd.qcut(q=4, duplicates="drop")`) and then one-hot encoded.
- **Top-3 feature selection** is done by `SelectFromModel(max_features=3)` *inside* the pipelines
  (cells 239, 240, 272, 273), so it is re-fitted in every cross-validation fold.
- **Brand/category inference (section 4, cells 23–53).** KNN classifiers are fitted on the
  validation table and evaluated on the same rows (cell 40: `fit(X_val_scaled, …)` then
  `predict(X_val_scaled)`), so the accuracies shown there are resubstitution accuracies. Cell 53
  then predicts brand and category for the 32 training runs (k = 4, distance-weighted) and stores
  them in `train_df`. These predicted labels are used in the plots of section 6 and dropped before
  modelling (cells 217 and 244). The scalers/PCA in this exploratory section are fitted outside
  pipelines.
- **Duplicate model key.** Cell 227 defines `pipelines['KNeighbors']` twice, so the second
  definition replaces the first: 19 distinct regressors are evaluated.
- **Randomness.** All estimators and splitters use `random_state=42` (168 occurrences). No global
  NumPy/Python seed is set. Results can still vary across library versions and platforms
  (see `docs/REPRODUCIBILITY.md`).
- **Small sample.** n = 32 runs of 26 vehicle-model codes; 6 models appear twice. The k-fold
  splits are by run, not by model, so runs of the same model can fall in both training and test
  folds.
