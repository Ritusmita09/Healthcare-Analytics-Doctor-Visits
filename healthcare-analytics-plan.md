# Healthcare Analytics for Doctor Visits — Project Plan

## Top-Level Overview

**Goal:** Build a complete, portfolio-ready healthcare analytics project using an authentic 5,190-row doctor-visits dataset. The project will produce a cleaned dataset, a Jupyter Notebook with exploratory data analysis, a Streamlit dashboard, a premium HTML/CSS/JS dashboard, and all supporting deployment and documentation files.

**Scope:** Purely descriptive/exploratory analytics. No causal claims. No synthetic data.

**Approach:** Phased, step-by-step delivery with user approval at each phase gate.

---

## Dataset Facts (Verified from CSV)

| Property | Value |
|---|---|
| File | `1776250375-P2-Healthcare Analytics for Doctor Visits.csv` |
| Total rows (data) | 5,190 |
| Total columns | 13 (1 unnamed index + 12 analytical) |
| First row is header | Yes |
| Unnamed column `""` | Row index (1–5190) — safe to drop |

---

## Data Dictionary

| Column | Raw Type | Meaning | Analytical Use | Notes / Limitations |
|---|---|---|---|---|
| *(unnamed)* | integer | Original row index in source | Drop — redundant with pandas index | Values 1–5190 |
| `visits` | integer | Number of doctor visits in the reference period | **Primary target variable** | Range seen: 0–14+; right-skewed; max value warrants inspection |
| `gender` | string | Patient gender | Demographic segmentation | Only "male" / "female" observed — binary representation |
| `age` | float | Patient age (appears to be a decimal fraction, not years) | Age-group analysis after transformation | Values like 0.19, 0.22, 0.72 — likely age divided by 100 or scaled; actual year = age × 100 |
| `income` | float | Household income (scaled/normalized) | Income-tier segmentation | Values 0–1.5; some zeros present; exact unit unknown |
| `illness` | integer | Number of illnesses/conditions in past 2 weeks | Health burden indicator | Range 0–5 observed; treat as ordinal count |
| `reduced` | integer | Number of days of reduced activity due to illness (past 2 weeks) | Activity limitation proxy | Range 0–14; 14 appears as a ceiling/maximum-coded value |
| `health` | integer | General health status (self-rated) | Subjective health score | Range 0–12+ observed; direction of scale needs assumption: higher = worse or better health |
| `private` | string | Whether the person has private health insurance | Insurance access segmentation | "yes" / "no" |
| `freepoor` | string | Whether covered by government free care (low-income) | Insurance access segmentation | "yes" / "no"; mutually exclusive intent with `private` |
| `freerepat` | string | Whether covered by government free care (repatriated/other) | Insurance access segmentation | "yes" / "no" |
| `nchronic` | string | Whether a non-limiting chronic condition is present | Chronic condition indicator | "yes" / "no" |
| `lchronic` | string | Whether a limiting chronic condition is present | Chronic condition severity indicator | "yes" / "no"; `lchronic=yes` implies more severe impact than `nchronic=yes` |

---

## Phase 1 Data Quality Findings

### 1. File Location and Size
- **Path:** `1776250375-P2-Healthcare Analytics for Doctor Visits.csv` (workspace root)
- **Rows:** 5,190 data rows + 1 header row = 5,191 total lines
- **Columns:** 13

### 2. Column List and Observed Types

| Column | Observed Type |
|---|---|
| *(unnamed index)* | integer string `"1"` – `"5190"` |
| `visits` | integer (0–14 observed range) |
| `gender` | string categorical: `"female"`, `"male"` |
| `age` | float: values in range ~0.19–0.72 |
| `income` | float: values in range 0–1.5 |
| `illness` | integer: values 0–5 observed |
| `reduced` | integer: values 0–14 (14 appears frequently — possible censoring ceiling) |
| `health` | integer: values 0–12 observed |
| `private` | string categorical: `"yes"`, `"no"` |
| `freepoor` | string categorical: `"yes"`, `"no"` |
| `freerepat` | string categorical: `"yes"`, `"no"` |
| `nchronic` | string categorical: `"yes"`, `"no"` |
| `lchronic` | string categorical: `"yes"`, `"no"` |

### 3. Missing Values
- **No blank/empty cells observed** in the rows sampled across the full file.
- Formal validation in Phase 2 will confirm with `df.isnull().sum()`.

### 4. Duplicate Rows
- Visual inspection reveals highly similar rows (e.g., multiple rows at `age=0.72`, `income=0.25`, `visits=0`) — these may be legitimate distinct patients with similar profiles, not duplicates.
- Phase 2 will run `df.duplicated().sum()` to report exact count.

### 5. Unique Values for Categorical Columns

| Column | Unique Values Observed |
|---|---|
| `gender` | `"female"`, `"male"` |
| `private` | `"yes"`, `"no"` |
| `freepoor` | `"yes"`, `"no"` |
| `freerepat` | `"yes"`, `"no"` |
| `nchronic` | `"yes"`, `"no"` |
| `lchronic` | `"yes"`, `"no"` |

### 6. Numerical Column Ranges (from file scan)

| Column | Min Observed | Max Observed | Notes |
|---|---|---|---|
| `visits` | 0 | 8 (seen: row 48); likely higher in full dataset | Right-skewed count variable |
| `age` | 0.19 | 0.72 | Scaled — multiply ×100 to interpret as years (19–72) |
| `income` | 0.00 | 1.50 | Scaled; 0 values present |
| `illness` | 0 | 5 | Appears capped at 5 |
| `reduced` | 0 | 14 | 14 appears repeatedly — likely a censoring cap (max recordable) |
| `health` | 0 | 12 | Direction of scale unclear without documentation |

### 7. Potential Outliers

- **`visits`**: Values of 7 and 8 observed early; full range likely extends higher. The right tail will be examined with a box plot and IQR rule.
- **`reduced`**: The value 14 appears very frequently — this is almost certainly the upper censoring limit of a "days in past 2 weeks" measurement, not a true data error.
- **`health`**: Values from 0 to 12 suggest a multi-point ordinal scale. Scale direction (does higher = better or worse health?) must be confirmed from dataset context.
- **`income = 0`**: Several rows have income = 0. These could be genuinely zero-income individuals or missing-coded-as-zero — requires investigation.

### 8. Data Quality Issues

| Issue | Severity | Action |
|---|---|---|
| Unnamed index column | Low | Drop during cleaning; it duplicates the pandas row index |
| `age` is scaled (not raw years) | Medium | Derive an `age_years` column = `age × 100` for interpretability |
| `reduced = 14` may be a censoring ceiling | Medium | Document; do not treat as outlier; consider as "14+" |
| `income = 0` rows | Medium | Flag; analyze separately; do not impute without evidence |
| `health` scale direction unknown | Medium | Document assumption; present both interpretations if ambiguous |
| Binary "yes"/"no" columns are strings | Low | Encode as 1/0 for correlation and modeling in Phase 2 |
| `visits = 0` constitutes a large proportion | Low-Medium | Verify whether zeros are "no visits" or "unknown"; highly relevant for analysis |

### 9. Index / Unnecessary Identifier Column
- The first unnamed column (quoted integers `"1"` to `"5190"`) is a row counter and should be dropped. It adds no analytical value.

### 10. Potential Analytical Relationships
- `visits` vs `illness` — more illnesses likely associated with more visits
- `visits` vs `reduced` — activity reduction may track healthcare utilization
- `visits` vs `lchronic` / `nchronic` — chronic conditions may drive repeat visits
- `visits` vs `age` — older patients may visit more frequently
- `visits` vs `income` — income may influence access to care
- `visits` vs insurance (`private`, `freepoor`, `freerepat`) — insurance type may affect visit counts
- `visits` vs `health` — poor self-rated health may correlate with more visits
- `gender` segmentation across all of the above

---

## Proposed Project Folder Structure

```
Healthcare-Analytics-Doctor-Visits/
│
├── data/
│   ├── raw/
│   │   └── doctor_visits_raw.csv          # Copy of original CSV (renamed, unmodified)
│   └── processed/
│       └── doctor_visits_clean.csv        # Cleaned dataset produced in Phase 2
│
├── notebooks/
│   └── healthcare_analytics.ipynb         # Full EDA Jupyter Notebook (Phase 3)
│
├── streamlit_app/
│   ├── app.py                             # Main Streamlit dashboard (Phase 4)
│   ├── requirements.txt                   # Python dependencies
│   └── assets/
│       └── style.css                      # Optional custom CSS
│
├── html_dashboard/
│   ├── index.html                         # Premium HTML dashboard (Phase 5)
│   ├── style.css
│   └── script.js
│
├── docs/
│   └── linkedin_summary.md                # LinkedIn project summary (Phase 6)
│
├── README.md                              # Professional GitHub README (Phase 6)
├── .gitignore
└── healthcare-analytics-plan.md           # This plan file
```

---

## Phased Implementation Plan

### Phase 1 — Dataset Inspection and Project Planning *(current phase)*
**Status:** `[-] in progress`
- Inspect raw CSV: columns, types, ranges, quality issues
- Build data dictionary
- Propose folder structure and plan
- **Gate:** User approval

### Phase 2 — Data Cleaning and Processed Dataset
**Status:** `[ ] pending`
- Create `data/raw/` and `data/processed/` folders
- Copy original CSV to `data/raw/doctor_visits_raw.csv` unchanged
- Write a Python cleaning script embedded in the notebook
- Drop the unnamed index column
- Derive `age_years` = `age × 100`
- Encode binary columns (`private`, `freepoor`, `freerepat`, `nchronic`, `lchronic`) as 0/1
- Flag `income = 0` rows
- Document `reduced = 14` as a censoring ceiling
- Verify and report: null counts, duplicate counts, final shape
- Save `data/processed/doctor_visits_clean.csv`
- **Gate:** User approval

### Phase 3 — Jupyter Notebook (EDA)
**Status:** `[ ] pending`
- Professional, well-commented `.ipynb` file
- Sections: Import → Load → Clean → Univariate → Bivariate → Multivariate → Insights
- All charts labeled, captioned, and styled
- Statistical summaries (describe, value_counts, crosstabs, correlation)
- Responsible framing: descriptive only, no causal language
- **Gate:** User approval

### Phase 4 — Streamlit Dashboard
**Status:** `[ ] pending`
- Multi-page or tabbed Streamlit app
- Interactive filters (gender, insurance, age group, chronic condition)
- Charts: visit distribution, age-visits, income-visits, illness-visits, insurance breakdown, chronic condition impact
- Summary statistics panel
- `requirements.txt` and deployment-ready configuration
- **Gate:** User approval

### Phase 5 — Premium HTML/CSS/JS Dashboard
**Status:** `[ ] pending`
- Standalone single-page dashboard (no server required)
- Data embedded as JSON or loaded from CSV
- Professional dark or light theme with healthcare color palette
- Charts via Chart.js or D3.js
- Responsive layout (mobile-friendly)
- GitHub Pages deployable
- **Gate:** User approval

### Phase 6 — README, LinkedIn Summary, and GitHub Packaging
**Status:** `[ ] pending`
- Professional `README.md` with badges, screenshots, dataset description, setup instructions
- `linkedin_summary.md` ready-to-paste post
- `.gitignore` for Python, Jupyter checkpoints, and node modules
- Final file structure review
- **Gate:** Final review

---

## Recommended Python Libraries

| Library | Purpose |
|---|---|
| `pandas` | Data loading, cleaning, transformation |
| `numpy` | Numerical operations |
| `matplotlib` | Base plotting |
| `seaborn` | Statistical visualization |
| `plotly` | Interactive charts (notebook + Streamlit) |
| `streamlit` | Dashboard framework |
| `scipy` | Descriptive statistics, IQR outlier detection |
| `jupyter` | Notebook environment |

---

## Analytical Questions to Investigate

1. What is the distribution of doctor visits? Is it heavily right-skewed (most people = 0–2 visits)?
2. How does the average number of visits differ between age groups?
3. Do patients with any illness report more visits than those with none?
4. Does the number of reduced-activity days correlate with visit counts?
5. Do patients with limiting chronic conditions (`lchronic=yes`) visit more than those with non-limiting ones?
6. How does private insurance coverage relate to visit frequency?
7. Are government-assisted patients (`freepoor`, `freerepat`) visiting at different rates than privately insured?
8. Does income level appear to relate to visit frequency?
9. Do gender differences appear in visit frequency or health indicators?
10. What combinations of conditions (illness + chronic + reduced) are associated with the highest visit counts?
11. What proportion of the dataset has zero visits? What characterizes the zero-visit group?
12. Is there a meaningful relationship between self-rated health score and visits?

---

## Limitations and Ethical Considerations

| Consideration | Detail |
|---|---|
| Causation vs. correlation | All findings are associational. No variable can be said to *cause* visit frequency. |
| `age` scale | Age appears scaled (0.19–0.72). Actual years must be inferred, not assumed. |
| `health` scale direction | Without metadata, it is unknown whether higher health scores mean better or worse health. Findings will note this assumption. |
| `reduced = 14` ceiling | Values of 14 represent "at least 14 days," not exactly 14. Analysis will treat this as censored. |
| `income = 0` | Could mean genuinely zero income or a missing-value code. Will not be imputed. |
| Binary gender representation | The dataset only records male/female; non-binary identities are absent. |
| Population and time context | The dataset origin (country, year, survey methodology) is not documented. Generalizations to any specific population are not supported. |
| No diagnostic codes | "illness" is a self-reported count, not a clinical classification. |

---

## Files to Create in Phase 2

1. `data/raw/doctor_visits_raw.csv` — original data, renamed and moved
2. `data/processed/doctor_visits_clean.csv` — cleaned output
3. `notebooks/healthcare_analytics.ipynb` — skeleton notebook with Phase 2 cleaning code
4. `streamlit_app/requirements.txt` — Python dependency list

---

## Sub-Tasks

### Sub-Task 1 — Phase 2: Data Cleaning
**Intent:** Produce a verified, cleaned dataset and populate the `data/` folder structure.
**Expected Outcomes:**
- `data/raw/doctor_visits_raw.csv` exists (copy of original, untouched)
- `data/processed/doctor_visits_clean.csv` exists with all cleaning steps applied
- Cleaning steps documented in the notebook
**Todo List:**
- [ ] Create folder structure: `data/raw/`, `data/processed/`, `notebooks/`, `streamlit_app/`, `html_dashboard/`, `docs/`
- [ ] Copy CSV to `data/raw/doctor_visits_raw.csv`
- [ ] Open notebook, load raw CSV
- [ ] Drop unnamed index column
- [ ] Derive `age_years` column
- [ ] Encode binary yes/no columns as 0/1
- [ ] Flag `income = 0` rows
- [ ] Run null check, duplicate check, shape report
- [ ] Save cleaned CSV
- [ ] Print data quality summary table
**Status:** `[ ] pending`

### Sub-Task 2 — Phase 3: Jupyter Notebook EDA
**Intent:** Produce a portfolio-quality notebook with full exploratory analysis.
**Status:** `[ ] pending`

### Sub-Task 3 — Phase 4: Streamlit Dashboard
**Intent:** Build an interactive Python dashboard.
**Status:** `[ ] pending`

### Sub-Task 4 — Phase 5: HTML/CSS/JS Dashboard
**Intent:** Build a standalone, GitHub Pages–ready visual dashboard.
**Status:** `[ ] pending`

### Sub-Task 5 — Phase 6: README and LinkedIn Summary
**Intent:** Complete the GitHub-ready project packaging.
**Status:** `[ ] pending`
