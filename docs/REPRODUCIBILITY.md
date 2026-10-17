# Reproducibility

## Original environment (from the notebook's own Colab log, cell 2)

Google Colab, Python 3.12, pandas 2.2.2, numpy 2.0.2, scipy 1.16.3, matplotlib 3.10.0,
plotly 5.24.1, lightgbm 4.6.0, catboost 1.2.8 (installed by the notebook), dataframe-image 0.2.7.
**Not recorded:** scikit-learn, xgboost, seaborn, umap-learn (pre-installed in Colab; warnings
were silenced, so the outputs give no version hint). The notebook also ran `apt-get install
chromium-chromedriver` for `dataframe-image`, but never calls `dfi.export`, so Chromium is not needed.

## Verification run

| Item | Value |
|---|---|
| Date | 2026-10-17 |
| OS | Windows 11 Pro (10.0.26300) |
| Python | 3.10.11 (isolated virtual environment) |
| Same as Colab | pandas 2.2.2, numpy 2.0.2, matplotlib 3.10.0, plotly 5.24.1, lightgbm 4.6.0, catboost 1.2.8, dataframe-image 0.2.7 |
| Different from Colab | scipy 1.15.3 (1.16.3 requires Python ≥ 3.11); Python 3.10 instead of 3.12 |
| Assumed (Colab version unknown) | scikit-learn 1.6.1, xgboost 3.1.1, seaborn 0.13.2, umap-learn 0.5.7 |
| Harness | `tests/run_notebook.py` (nbclient 0.11.0, ipykernel 7.3.0); notebook not modified |

## Results of the verification run

Command: `python tests/run_notebook.py --keep tests/_run`. All 212 code cells executed in order in
385 s with **no errors**. The stored outputs of the original Colab run were compared cell by cell
(text output and contents of HTML tables; figures and Plotly charts not compared):

| Outcome | Code cells |
|---|---|
| Identical | 56 |
| Numerically equal at the displayed precision (last-digit float round-off only: cells 26, 30, 32) | 3 |
| Different | 4 (cells 233, 266, 275, 276 — see below) |
| No reference: output hidden in the original notebook ("Output hidden; open in Colab") | 2 (cells 230, 240) |
| Environment log only (`!pip` / `!apt-get`, cell 2) | 1 |
| No text output (plots, assignments, definitions) | 146 |

Reproduced exactly include: data cleaning and renaming, descriptive statistics, the Pearson
correlation table (±0.35 threshold), the multi-output and single-output regression and
classification metric tables (cells 231, 238, 239, 262–264, 271–273) and the final summary table
(cells 275–276, manuscript Table 4) except the entries below.

| Cell | Content | Original | Re-run |
|---|---|---|---|
| 275, 276 | Final summary (Table 4 in the manuscript; regression = R², classification = weighted F1): Gaussian Process regression — Multi-Output / All features | −7.6451 | −7.6450 |
| 275, 276 | same — Single-Output / All features | −7.5297 | −7.5334 |
| 233 | Regression with PCA (3 components), LightGBM: R² / RMSE / MAE (SAE points) | −0.79 / 0.48 / 0.39 | −0.71 / 0.47 / 0.38 |
| 266 | Classification with PCA, Accuracy / Precision / Recall / F1 (weighted) | LightGBM 0.4688 / 0.4700 / 0.4688 / 0.4652; KNeighbors 0.4911 / 0.4428 / 0.4911 / 0.4565 | LightGBM 0.4732 / 0.4823 / 0.4732 / 0.4744; KNeighbors 0.5000 / 0.4532 / 0.5000 / 0.4640 (row order changes accordingly) |

All other values in these four cells are identical.

**Interpretation (not verified further).** The Gaussian Process regressor optimises its kernel
with SciPy's L-BFGS-B, and SciPy is the one recorded library whose version could not be matched
(1.15.3 vs 1.16.3), together with the operating system and Python version. The PCA-based
variants are sensitive to floating-point differences in the decomposition. Re-running in
Google Colab, or with Python ≥ 3.11 and `scipy==1.16.3`, is the way to confirm this; it was not
possible on the verification machine.

**Conclusion.** The published notebook runs end to end without modification and reproduces the
reported results, with the exceptions listed above. Exact agreement is not claimed for the
Gaussian Process regression entries of Table 4 or for the PCA-based variants.
