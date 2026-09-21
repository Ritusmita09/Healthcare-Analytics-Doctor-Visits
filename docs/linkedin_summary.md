# LinkedIn Project Summary

> Copy-paste this post to LinkedIn when publishing your project. Edit any bracketed placeholders before posting.

---

## 📋 Post Option A — Concise (Recommended)

---

🏥 **Just completed a full end-to-end Healthcare Analytics project — from raw data to interactive dashboard!**

I built a portfolio project analysing **doctor visit patterns** across 5,190 survey respondents using a real-world health economics dataset.

**What I built:**
✅ Data cleaning & feature engineering pipeline (Python / pandas)
✅ Exploratory Data Analysis notebook with 12 analytical questions
✅ Interactive Streamlit dashboard (8 pages, live filters)
✅ Standalone HTML/CSS/JS dashboard (Plotly, no server required)
✅ Full GitHub-ready project with README and documented methodology

**Key findings (descriptive, not causal):**
📊 79.8% of respondents reported zero doctor visits in the reference period
📊 Respondents with any illness reported 3× more visits on average
📊 Activity-limiting conditions were associated with significantly higher utilisation
📊 Free-repeat-prescription holders showed the highest mean visit counts among insurance groups
📊 A weak positive association exists between age-band and visit frequency (ρ = 0.15)

**Tech stack:** Python · pandas · NumPy · SciPy · Matplotlib · Seaborn · Plotly · Streamlit · HTML · CSS · JavaScript

**Methodological note:** All findings are observational and descriptive. No causal relationships are claimed. Statistical tests were used for pattern identification, not hypothesis confirmation.

🔗 GitHub: [your-github-url]
🔗 Live Dashboard: [your-github-pages-url]

\#HealthcareAnalytics \#DataScience \#Python \#Streamlit \#DataVisualization \#Portfolio \#PublicHealth \#EDA \#OpenSource

---

## 📋 Post Option B — Detailed (For technical audiences)

---

🔬 **Healthcare Analytics for Doctor Visits — A complete data science portfolio project**

After completing this end-to-end analytics project, I wanted to share both the methodology and the technical decisions behind it.

**The Dataset**
5,190 survey respondents · 12 original variables · Australian health economics context
Variables include: visit counts, demographics (age, gender), health status indicators (illness, reduced activity days, self-assessed health), insurance type (private, free-poor, free-repeat), income, and chronic condition flags.

**Data Quality Challenges Solved**
- Zero-inflation: 79.8% of respondents reported 0 visits — standard outlier removal was inappropriate; instead, visit tiers were engineered (None / Low / Moderate / High)
- Age stored as scaled decimal (0.19–0.72) — decoded into discrete year-bands (19–72)
- Insurance columns were mutually exclusive across all rows — validated and used to create a unified insurance_type feature
- 1,320 apparent duplicate rows were retained as legitimate independent respondents after domain review
- Income = 0 (79 rows) was ambiguous — preserved and flagged rather than imputed

**Analytical Questions Explored**
1. How do visits distribute across the population? (zero-inflated, right-skewed)
2. How does illness status relate to visit frequency?
3. How do activity-limitation days correlate with visits?
4. How does self-assessed health score vary across visit tiers?
5. How do age-bands differ in utilisation?
6. How does gender compare in visit patterns?
7. How do insurance types compare?
8. How does income relate to visits?
9. How do chronic conditions relate to utilisation?
10. What combinations of risk factors predict higher utilisation?
11. How do high utilisers differ from zero-visit respondents?
12. What does a composite vulnerability index reveal?

**Statistical Methods Used**
- Spearman rank correlation (non-parametric, appropriate for skewed data)
- Kruskal-Wallis H-test (group comparisons, non-normal distributions)
- Mann-Whitney U-test (two-group comparisons)
- Descriptive statistics with explicit limitation disclosures

**Dashboards Built**
- Streamlit: 8 pages, live sidebar filters, Plotly charts, cached data loader
- HTML/JS: Fully standalone (PapaParse + Plotly CDN), deployable to GitHub Pages without a server

**Ethical Considerations Documented**
- No causal claims made anywhere in the project
- Health score directionality explicitly noted as unknown
- Aggregated reporting only — no individual-level inference
- Income and insurance variables treated with socioeconomic sensitivity

🔗 GitHub: [your-github-url]
🔗 Live Dashboard: [your-github-pages-url]
🔗 Notebook (nbviewer): [your-nbviewer-url]

\#DataScience \#HealthcareAnalytics \#Python \#Streamlit \#EDA \#Statistics \#Portfolio \#PublicHealth \#DataEngineering \#Plotly

---

## 📋 Short Comment Reply (For when someone asks about your project)

---

Thanks! This was a full end-to-end healthcare analytics project — data cleaning, EDA notebook, Streamlit dashboard, and a standalone HTML dashboard, all built from a real health survey dataset. The most interesting challenge was handling the zero-inflated visit distribution (80% of respondents had zero visits) without distorting the analysis. Happy to share more details or the GitHub link!

---

## 📋 Resume / Portfolio Bullet Points

Add these to your resume under a **Projects** section:

```
Healthcare Analytics for Doctor Visits                              [Year]
Tools: Python, pandas, NumPy, SciPy, Matplotlib, Seaborn, Plotly, Streamlit, HTML/CSS/JS

• Cleaned and engineered a 5,190-row health survey dataset across 26 features using pandas,
  resolving zero-inflation, scaled age encoding, and mutually exclusive insurance flags.

• Conducted exploratory data analysis across 12 analytical questions using Spearman
  correlation, Kruskal-Wallis, and Mann-Whitney U statistical tests.

• Built an 8-page interactive Streamlit dashboard with live sidebar filters and Plotly charts,
  deployed via Streamlit Cloud.

• Built a standalone HTML/CSS/JS dashboard using PapaParse and Plotly, deployed to GitHub
  Pages with no server dependency.

• Documented methodology, ethical considerations, and observational limitations throughout
  the notebook and dashboard, following responsible analytics practices.
```

---

## 📋 Deployment Links to Fill In

| Resource | URL |
|---|---|
| GitHub Repository | `https://github.com/[username]/Healthcare-Analytics-Doctor-Visits` |
| GitHub Pages Dashboard | `https://[username].github.io/Healthcare-Analytics-Doctor-Visits/` |
| Streamlit Cloud App | `https://[app-name].streamlit.app` |
| Notebook on nbviewer | `https://nbviewer.org/github/[username]/Healthcare-Analytics-Doctor-Visits/blob/main/notebooks/healthcare_analytics.ipynb` |

---

*Replace all `[bracketed]` placeholders before publishing.*
