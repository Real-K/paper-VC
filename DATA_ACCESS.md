# Data access

None of the primary sources can be redistributed in this repository. This file states what each contains, what it is used for, and how to obtain it.

| Source | Used for | Redistributable here | How to obtain |
|---|---|---|---|
| **Crunchbase** full data dump (19 relational tables: organizations, people, jobs, funding rounds, investments, investment partners, investors, funds, acquisitions, IPOs, …) | Everything: the partner-attributed deal sample, founder and partner gender, sectors, stages, exits, follow-on rounds, syndicates | **No** — licensed | Crunchbase data licence (research or enterprise access); the pipeline expects the CSV export in `CRUNCHBASE_RAW` |
| **cores_v1** and **sample_v1.parquet** (derived from the dump) | The frozen analysis file: 154,123 partner-attributed deals, 2010-01 to 2023-10 | **No** — derived from licensed microdata (row-level identifiers) | Rebuild with `code/pipeline/build_cores.py` then `build_sample_v1.py`; the SHA-256 prefix and row count to match are in `artifacts/sample_manifest.yaml` |
| **SEC Form D** structured data sets (FORMDSUBMISSION, ISSUERS, OFFERING, RECIPIENTS, RELATEDPERSONS, SIGNATURES) | Fund-cycle controls and Form D coverage in `p001_58` | Raw files are public but not copied here (size); the fund-vehicle ↔ investor match tables are not copied (firm identifiers) | https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets — quarterly ZIPs; `code/public_sources/fetch_sec_formd.py` downloads them (declare a contact in `SEC_CONTACT`), `build_formd_v1.py` parses, `match_formd_funds_v2.py` matches |
| **Companies House** officers (UK) | Partner-level checks for UK firms | **No** — officer-level records | Free REST API key (https://developer.company-information.service.gov.uk/); `CH_API_KEY`; `code/public_sources/ch_fetch_officers.py` |
| **USPTO PatentsView** bulk files (g_/pg_ application and assignee tables) | Prior patent applications of portfolio companies (balance test; within-partner control) | Public but not copied (size); the company ↔ assignee match tables are not copied (company identifiers) | https://patentsview.org/download/data-download-tables → `USPTO_RAW`; `build_patents_v1.py`, `build_patents_dim.py`, `match_patents_companies_v2.py` |
| **Crunchbase funds** table | Fund age, size and sequence controls | **No** — part of the dump | `build_cb_funds_v1.py` |

## What *is* here instead

`artifacts/` holds the aggregate result files (JSON) written by every analysis run: coefficients, bootstrap intervals, minimum detectable effects, permutation p-values, cell and deal counts, balance statistics, decomposition components. They contain no company, person, round or investor identifiers (the assembly script asserts this), and they are the only inputs the exhibit generator and the notebooks need.

Entity-level derived files — the analysis parquet, matched fund vehicles, matched patent assignees, officer lists, PitchBook request lists — are **deliberately excluded**: they derive from licensed or person-level sources and would identify firms and people.

## Reproducing from raw data

`code/pipeline/` is the complete analysis chain: `build_cores.py` → `build_sample_v1.py` → the pre-study harness `i73 … i82` → the paper's runs `p001_00 … p001_59`. With the Crunchbase export in place and the environment variables set (`README.md`), each script writes its JSON artifact into `P001_OUT`; `code/build/p001_09_exhibits.py` then regenerates the exhibits from those artifacts, and `notebooks/01_tables.ipynb` compares them with the paper's.
