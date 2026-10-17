# Release and Zenodo archiving procedure

Zenodo archives a GitHub repository when a **GitHub release** is published while the
GitHub–Zenodo integration is enabled for that repository. A `git push` alone is not archived.
`CITATION.cff` supplies the metadata; no `.zenodo.json` is used, because the CFF file covers every
field needed. Note that a `.zenodo.json`, if added, would take precedence over `CITATION.cff`.

## Prerequisites (in this order)

1. Publication scope and data authorisation decided (`docs/PUBLICATION_AUDIT.md`).
2. Licences: the code is MIT (`LICENSE`, `license: MIT` in `CITATION.cff`). The data have no reuse
   licence; on Zenodo, state this in the record description so that it is not read as CC BY data.
3. All checks pass: `python tests/check_integrity.py`, `python tests/check_environment.py`,
   `python tests/check_repository.py`.
4. Repository made public on GitHub. Zenodo can archive private repositories, but a public
   archive of non-public data must be avoided.

## Steps that need the owner's accounts (manual)

1. Sign in at <https://zenodo.org> with the GitHub account `EngSarzedas` ("Log in with GitHub")
   and link the ORCID iD in the Zenodo profile.
2. Zenodo → *GitHub* (account menu) → *Sync now* → switch **on** `EngSarzedas/Subjective-Ride-Comfort-ML`.
   This must happen **before** the release is created.
3. On GitHub: *Releases* → *Draft a new release* → tag `v1.0.0` on `main`, title
   `v1.0.0 — material associated with the manuscript`, short notes, then *Publish release*.
   Equivalent CLI: `gh release create v1.0.0 --title "v1.0.0" --notes "…"`.
4. On Zenodo, open the new record and check the title, authors, ORCID, licence, keywords and file list.
   **Licence caveat:** a Zenodo record carries a single licence, taken from `CITATION.cff` (MIT).
   Because the archive also contains the data, which have no reuse licence, decide **before step 3**
   whether to (a) obtain a data licence from the owner and describe both licences in the record,
   (b) archive the data as a separate Zenodo record with its own access conditions, or (c) edit
   the record description to state that MIT covers the code only.
5. Record both identifiers Zenodo shows:
   - **Version DOI**: refers to exactly `v1.0.0`. Cite this one in the article for reproducibility.
   - **Concept DOI**: always resolves to the latest version.
6. Add the DOIs to `README.md` (Citation section) and `CITATION.cff` (`doi:` for the version DOI,
   or `identifiers:` for both). Then commit with `git commit -m "Add Zenodo DOIs"`. Do not tag that
   commit as v1.0.0: the archived v1.0.0 stays as it was.

## If the data cannot be public

Release only the code-only variant, or create the Zenodo record manually with *restricted access*
for the data. In that case the record must not describe the data as openly available.
