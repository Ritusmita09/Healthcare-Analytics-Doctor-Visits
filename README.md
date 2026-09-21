# Healthcare Analytics for Doctor Visits

An end-to-end data analytics project covering data cleaning, exploratory data analysis, statistical testing, and interactive dashboard development — built on an authentic healthcare survey dataset of 5,190 respondents.

> **Scope:** This is an academic and portfolio project. All findings are descriptive associations derived from survey data. No causal relationships are established and no medical advice is given.

---

## Contents

- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Dataset Description](#dataset-description)
- [Data Dictionary](#data-dictionary)
- [Project Structure](#project-structure)
- [Data Cleaning Methodology](#data-cleaning-methodology)
- [EDA Methodology](#eda-methodology)
- [Statistical Tests](#statistical-tests)
- [Key Findings](#key-findings)
- [Dashboards](#dashboards)
- [Local Setup](#local-setup)
- [GitHub Pages Deployment](#github-pages-deployment)
- [Data Limitations and Ethical Considerations](#data-limitations-and-ethical-considerations)
- [Future Improvements](#future-improvements)

---

## Problem Statement

Healthcare utilization patterns — specifically doctor visit frequency — are shaped by a complex mix of health status, demographics, insurance coverage, and socioeconomic factors. Understanding these patterns through exploratory analysis can surface associations worth investigating further through rigorous research.

This project applies a structured EDA workflow to a real survey dataset to identify observable patterns in doctor visit frequency across demographic and health-related subgroups.

---

## Project Objectives

1. Clean and validate an authentic healthcare survey dataset.
2. Perform complete exploratory data analysis with verified statistical summaries.
3. Identify observable associations between doctor visits and health, demographic, and insurance variables.
4. Communicate findings responsibly — without causal language or unsupported medical conclusions.
5. Deliver two professional interactive dashboards (Streamlit and HTML/JS).

---

## Dataset Description

| Property | Value |
|---|---|
| **Raw file** | `data/raw/doctor_visits_raw.csv` |
| **Original source file** | `1776250375-P2-Healthcare Analytics for Doctor Visits.csv` |
| **Rows** | 5,190 |
| **Original columns** | 13 (including 1 redundant row-index column) |
| **Analytical columns** | 12 |
| **Missing values** | 0 |
| **Duplicate rows (on 12 original columns)** | 1,320 (retained — see [Data Limitations](#data-limitations-and-ethical-considerations)) |
| **Likely provenance** | Consistent with Cameron & Trivedi (1986) Australian health survey. Country, year, and survey methodology are not confirmed in the file itself. |

---

## Data Dictionary

### Original Columns

| Column | Type | Meaning | Notes |
|---|---|---|---|
| `visits` | integer | Number of doctor visits in the reference period | Target variable; range 0–9; zero-inflated |
| `gender` | string | Respondent gender | `"female"` / `"male"` only |
| `age` | float | Age scaled as decimal (0.19–0.72) | 12 discrete bands; multiply × 100 for year-band label |
| `income` | float | Household income, normalized (0.00–1.50) | 14 discrete levels; 79 rows have income = 0 (ambiguous) |
| `illness` | integer | Self-reported illness count, past 2 weeks | 0–5; not clinically coded |
| `reduced` | integer | Days of reduced activity, past 2 weeks | 0–14; value 14 = measurement ceiling |
| `health` | integer | Self-rated health score | 0–12; **scale direction not documented** |
| `private` | string | Has private health insurance | `"yes"` / `"no"` |
| `freepoor` | string | Government free care — low-income scheme | `"yes"` / `"no"` |
| `freerepat` | string | Government free care — repatriated/veterans scheme | `"yes"` / `"no"` |
| `nchronic` | string | Non-limiting chronic condition present | `"yes"` / `"no"` |
| `lchronic` | string | Limiting chronic condition present | `"yes"` / `"no"` |

### Engineered Columns (added in cleaning)

| Column | Meaning |
|---|---|
| `age_years` | `age × 100` — human-readable year-band |
| `age_group` | Six analysis bands: `<=25`, `26-35`, `36-45`, `46-55`, `56-65`, `66+` |
| `income_zero_flag` | 1 if `income == 0` |
| `income_group` | Four income tiers: Low / Lower-Mid / Upper-Mid / High |
| `*_enc` | Binary 0/1 encodings of all yes/no columns |
| `insurance_type` | Single derived category: `Private` / `Free-Poor` / `Free-Repatriated` / `Uninsured` |
| `chronic_status` | Severity hierarchy: `No Condition` / `Non-Limiting` / `Limiting` |
| `visit_group` | Utilization bands: `0 visits` / `1-2 visits` / `3-5 visits` / `6+ visits` |
| `reduced_at_ceiling` | 1 if `reduced == 14` |

---

## Project Structure

```
Healthcare-Analytics-Doctor-Visits/
│
├── data/
│   ├── raw/
│   │   └── doctor_visits_raw.csv          # Original CSV — never modified
│   └── processed/
│       ├── doctor_visits_clean.csv        # Cleaned dataset (5,190 × 26)
│       └── fig*.png                       # EDA chart exports from the notebook
│
├── notebooks/
│   └── healthcare_analytics.ipynb         # Complete EDA notebook (59 cells)
│
├── streamlit_app/
│   ├── app.py                             # Main entry point
│   ├── data_loader.py                     # Cached data loader + filter logic
│   ├── requirements.txt                   # Python dependencies
│   ├── .streamlit/
│   │   └── config.toml                    # Healthcare blue theme
│   └── app_pages/                         # 8 dashboard page modules
│       ├── overview.py
│       ├── visit_patterns.py
│       ├── demographics.py
│       ├── health_burden.py
│       ├── insurance_income.py
│       ├── relationships.py
│       ├── key_insights.py
│       └── limitations.py
│
├── html_dashboard/
│   ├── index.html                         # Standalone HTML dashboard
│   ├── style.css
│   └── script.js
│
├── docs/
│   └── linkedin_summary.md                # LinkedIn post draft
│
├── index.html                             # GitHub Pages redirect to html_dashboard/
├── .nojekyll                              # Disables Jekyll on GitHub Pages
├── .gitignore
├── healthcare-analytics-plan.md           # Project planning document
└── README.md                              # This file
```

---

## Data Cleaning Methodology

All cleaning was performed in [`notebooks/healthcare_analytics.ipynb`](notebooks/healthcare_analytics.ipynb). The raw file is preserved unchanged at [`data/raw/doctor_visits_raw.csv`](data/raw/doctor_visits_raw.csv).

### Cleaning Decisions

| Decision | Reason |
|---|---|
| **Dropped `Unnamed: 0`** | Confirmed sequential row counter 1–5190; no analytical value |
| **No rows removed** | All 5,190 rows retained — zero-visit records are valid survey responses |
| **1,320 duplicate profiles retained** | With only 12 attributes (binary yes/no + discrete age/income bands), identical profiles across distinct respondents are expected |
| **`age_years = age × 100`** | Raw 0.19–0.72 values are 12 discrete year-bands; multiply × 100 for interpretability |
| **`reduced = 14` preserved** | Measurement ceiling in a 2-week window; 188 rows flagged with `reduced_at_ceiling` |
| **`income = 0` preserved** | Ambiguous (true zero or missing code); 79 rows flagged with `income_zero_flag` |
| **Binary columns encoded as 0/1** | Enables numerical correlation analysis alongside original string columns |
| **`insurance_type` derived** | Single 4-category column from the three mutually exclusive insurance columns |
| **`chronic_status` derived** | Ordered severity: `No Condition` → `Non-Limiting` → `Limiting` |
| **`chronic_status = "No Condition"` (not `"None"`)** | Avoids CSV null round-trip bug in Python/pandas |

---

## EDA Methodology

The notebook is organized into 13 sections across 59 cells (32 markdown + 27 code). Key analytical steps:

1. Raw data inspection — shape, types, missing values, duplicates, value ranges
2. Feature validation — all engineered columns verified with assertions against source columns
3. Univariate analysis — distributions for all 12 original variables
4. Bivariate analysis — `visits` vs each predictor variable
5. Multivariate — Spearman correlation matrix, group profiling (zero vs. high-utilizer)
6. All charts produced with Matplotlib and Seaborn; saved to `data/processed/`

Visualizations include: visit histogram, boxplot, illness-visits bar chart, reduced-activity scatter, chronic-status comparison, insurance-type comparison, gender comparison, age-group heatmap, and a 12×12 Spearman correlation heatmap.

---

## Statistical Tests

Non-parametric tests were used throughout because `visits` is a zero-inflated integer count variable that violates normality assumptions.

| Test | Variables Compared | Purpose |
|---|---|---|
| **Spearman rank correlation** | `reduced`, `illness`, `health`, `age_years`, `income` vs `visits` | Measure monotonic association without assuming normality |
| **Kruskal-Wallis H test** | `chronic_status` groups vs `visits` | Test whether visit distributions differ across 3+ groups |
| **Kruskal-Wallis H test** | `insurance_type` groups vs `visits` | Test whether visit distributions differ across insurance types |
| **Mann-Whitney U test** | Government-assisted vs Private vs `visits` | Compare two independent group distributions |
| **Mann-Whitney U test** | Female vs Male vs `visits` | Compare visit distributions between gender groups |

> All p-values reported at α = 0.05. Statistical significance does not imply causation.

---

## Key Findings

All findings below are computed from the dataset. They are descriptive associations — not causal explanations.

### Visit Distribution
- **79.8% of respondents report zero doctor visits** in the reference period (4,141 of 5,190).
- Mean visits = **0.302**; median = **0**; maximum = **9**. The distribution is strongly right-skewed.
- Only **93 respondents (1.8%)** report 3 or more visits.

### Demographic Patterns
- Mean visits increases with age: **0.206** (age ≤25) to **0.454** (age 66+); Spearman rho = **0.148**.
- Female respondents show higher mean visits (**0.362**) than male (**0.236**). Spearman rho with gender (male=1) = −0.108. This is an observed difference; no biological or causal explanation is made.

### Health Burden
- **Reduced-activity days** is the strongest correlate with visits: Spearman rho = **0.336**.
- **Illness count** shows a monotonic association: mean visits rises from 0.079 (illness = 0) to 0.814 (illness = 5); Spearman rho = **0.263**.
- **Limiting chronic conditions** are associated with the highest mean visits (**0.603**) vs. no condition (**0.192**). Kruskal-Wallis H = 170.6, p < 0.001.
- **Health score**: Spearman rho = **0.178**. Scale direction is not documented — no directional medical claim is made.

### Insurance and Income
- **Free-Repatriated** respondents show the highest mean visits (**0.467**); **Free-Poor** the lowest (0.158).
- The three insurance columns (`private`, `freepoor`, `freerepat`) are perfectly mutually exclusive across all 5,190 rows.
- **Income**: Spearman rho = −0.093 — a very weak negative association. Practical effect size is small.

---

## Dashboards

### Streamlit Dashboard

An interactive multi-page dashboard built with Streamlit and Plotly.

**Pages:** Overview · Visit Patterns · Demographics · Health Burden · Insurance & Income · Relationships · Key Insights · Data Limitations

**Sidebar filters:** Gender · Age group · Insurance type · Chronic status · Visit group · Illness count range · Reset button

All KPI cards and charts update dynamically when filters change.

#### Launch (from the project root)

```bash
python -m streamlit run streamlit_app/app.py
```

Opens at **http://localhost:8501**

#### Dependencies

```bash
pip install -r streamlit_app/requirements.txt
```

---

### HTML / CSS / JavaScript Dashboard

A standalone, responsive web dashboard. No server-side language required after deployment.

**Pages:** Overview · Visit Patterns · Demographics · Health Burden · Insurance & Income · Relationships · Key Insights · Data Limitations

**Libraries:** [Plotly.js](https://plotly.com/javascript/) (charts), [PapaParse](https://www.papaparse.com/) (CSV parsing)

**Charts:** 27 interactive Plotly charts including histograms, bar charts, boxplots, donut charts, heatmaps, and scatter plots.

> **Important:** The HTML dashboard fetches the CSV file at runtime. It must be served via a local HTTP server or GitHub Pages. Opening `index.html` directly from the file system (`file://`) will fail due to browser security restrictions.

#### Launch via Python HTTP server (from the project root)

```bash
python -m http.server 8080
```

Then open: **http://localhost:8080/html_dashboard/**

#### Launch via VS Code Live Server

Right-click `html_dashboard/index.html` → **Open with Live Server**

---

## Local Setup

### Prerequisites

- Python 3.9 or later
- pip

### Install dependencies

```bash
pip install -r streamlit_app/requirements.txt
```

### Run the Jupyter Notebook

```bash
jupyter notebook notebooks/healthcare_analytics.ipynb
```

Or using JupyterLab:

```bash
jupyter lab notebooks/healthcare_analytics.ipynb
```

---

## GitHub Pages Deployment

GitHub Pages can serve the HTML dashboard as a static site directly from the repository.

### Steps

1. Push the repository to GitHub (see Git commands below).
2. Go to **Settings → Pages** in your GitHub repository.
3. Set **Source** to `Deploy from a branch`.
4. Set **Branch** to `main` (or `master`) and the folder to `/ (root)`.
5. Save. GitHub Pages will build and publish the site.

Once published, the dashboard will be accessible at:

```
https://<your-github-username>.github.io/<repository-name>/
```

The root [`index.html`](index.html) automatically redirects to `html_dashboard/index.html`.

A [`.nojekyll`](.nojekyll) file is included to prevent GitHub Pages from running Jekyll processing, which would interfere with Python `__pycache__` directories and paths beginning with underscores.

> **Note:** GitHub Pages will serve the pre-computed `data/processed/doctor_visits_clean.csv` as a static file. The JavaScript dashboard fetches this CSV at page load. No server-side processing is required.

### Git commands (run manually after reviewing)

```bash
# Configure your identity if not already done
git config user.name "Your Name"
git config user.email "your@email.com"

# Stage all project files
git add .

# Create the initial commit
git commit -m "Initial commit: Healthcare Analytics for Doctor Visits (Phase 1-6 complete)"

# Add your GitHub remote (replace with your actual repository URL)
git remote add origin https://github.com/<your-username>/Healthcare-Analytics-Doctor-Visits.git

# Push to GitHub
git push -u origin master
```

> Review the staged files with `git status` before committing. Do not force-push unless you understand the consequences.

---

## Data Limitations and Ethical Considerations

| Limitation | Detail |
|---|---|
| **Zero-inflated visits** | 79.8% of respondents report 0 visits. Group medians = 0 for most subgroups; means are not representative. |
| **Right-skewed distribution** | IQR = 0; standard outlier rules do not apply. |
| **`reduced = 14` ceiling** | 188 rows hit the 2-week maximum. True values beyond 14 are unknown. |
| **`income = 0` ambiguity** | 79 rows — genuine zero income vs. missing code undetermined. |
| **`health` scale direction** | Not documented. Higher may mean better or worse health. No directional claim is made. |
| **Self-reported variables** | `illness`, `health`, and `reduced` are subjective; not clinically verified. |
| **Binary gender** | Only female and male recorded. Non-binary identities are absent. |
| **Dataset provenance** | Country, year, and survey methodology not confirmed in the file. |
| **Identical attribute rows** | 1,320 duplicated profiles are retained as distinct respondents. |
| **Correlation ≠ causation** | All findings are observational. No causal inference is made or implied. |

---

## Future Improvements

- Zero-inflated count models (ZIP or ZINB regression) to separately model the zero-visit and positive-visit processes
- Stratified analysis to examine how associations change within specific age or insurance subgroups
- Bootstrap confidence intervals on group mean differences
- Unsupervised clustering to identify respondent profiles
- Interactive filters in the HTML dashboard (currently filtered server-side in Streamlit only)
- Confirmation of dataset provenance and addition of temporal or geographic context if available

---

## Author

*(Add your name, GitHub profile link, and LinkedIn profile link here)*

---

## License

This project is for academic and portfolio purposes. The dataset is used for educational analysis only. If you use this work, please credit the original source and note that no clinical or policy conclusions should be drawn from this exploratory analysis.
