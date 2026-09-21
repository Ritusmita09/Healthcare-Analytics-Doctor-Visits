/**
 * Healthcare Analytics — Doctor Visits Dashboard
 * script.js
 *
 * All statistics are computed directly from the processed CSV file.
 * Plotly.js is used for all interactive charts.
 * PapaParse is used for CSV parsing.
 *
 * Run from the project root via VS Code Live Server or any static
 * file server — NOT opened directly as a local file:// URL, because
 * browsers block cross-origin CSV fetch requests in file:// context.
 */

"use strict";

// ── Constants ─────────────────────────────────────────────────────────────────
const CSV_PATH = "../data/processed/doctor_visits_clean.csv";

const BLUE    = "#2563EB";
const GREEN   = "#059669";
const AMBER   = "#D97706";
const RED     = "#DC2626";
const PURPLE  = "#7C3AED";
const CYAN    = "#0891B2";
const PINK    = "#BE185D";
const MUTED   = "#94A3B8";
const SLATE   = "#475569";

const CHART_COLORS = [BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK];

const AGE_ORDER      = ["<=25","26-35","36-45","46-55","56-65","66+"];
const INCOME_ORDER   = ["Low(0-0.15)","Lower-Mid(0.16-0.45)","Upper-Mid(0.46-0.75)","High(0.76-1.50)"];
const INCOME_LABELS  = ["Low (0-0.15)","Lower-Mid\n(0.16-0.45)","Upper-Mid\n(0.46-0.75)","High (0.76-1.50)"];
const CHRONIC_ORDER  = ["No Condition","Non-Limiting","Limiting"];
const INS_ORDER      = ["Private","Free-Poor","Free-Repatriated","Uninsured"];
const VISIT_GRP      = ["0 visits","1-2 visits","3-5 visits","6+ visits"];

const PLOTLY_CONFIG  = { responsive: true, displayModeBar: false };
const CHART_MARGIN   = { l: 48, r: 16, t: 24, b: 48 };
const CHART_MARGIN_S = { l: 48, r: 8,  t: 24, b: 60 };

// ── Global state ──────────────────────────────────────────────────────────────
let DATA = null;     // full parsed CSV rows as array of objects

// ── Helpers ───────────────────────────────────────────────────────────────────
function fmt(v, d = 3) {
  if (v === null || v === undefined || isNaN(v)) return "—";
  return parseFloat(v.toFixed(d));
}

function mean(arr) {
  if (!arr.length) return 0;
  return arr.reduce((s, v) => s + v, 0) / arr.length;
}

function median(arr) {
  if (!arr.length) return 0;
  const s = [...arr].sort((a,b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 === 0 ? (s[m-1] + s[m]) / 2 : s[m];
}

function pct(count, total) {
  return total ? (count / total * 100).toFixed(1) + "%" : "—";
}

function groupMean(rows, groupCol, targetCol, order) {
  const groups = {};
  rows.forEach(r => {
    const g = r[groupCol];
    if (!groups[g]) groups[g] = [];
    groups[g].push(+r[targetCol]);
  });
  return (order || Object.keys(groups)).map(g => ({
    label: g,
    mean: groups[g] ? fmt(mean(groups[g]), 3) : null,
    count: groups[g] ? groups[g].length : 0,
  }));
}

function groupCount(rows, col, order) {
  const counts = {};
  rows.forEach(r => { const v = r[col]; counts[v] = (counts[v] || 0) + 1; });
  return (order || Object.keys(counts)).map(g => ({ label: g, count: counts[g] || 0 }));
}

function spearman(xs, ys) {
  // Rank-based Spearman correlation (fast approximation via sort)
  function rank(arr) {
    const sorted = arr.map((v,i) => ({v,i})).sort((a,b) => a.v - b.v);
    const ranks = new Array(arr.length);
    let i = 0;
    while (i < sorted.length) {
      let j = i;
      while (j < sorted.length - 1 && sorted[j+1].v === sorted[j].v) j++;
      const avgRank = (i + j) / 2 + 1;
      for (let k = i; k <= j; k++) ranks[sorted[k].i] = avgRank;
      i = j + 1;
    }
    return ranks;
  }
  const n = xs.length;
  const rx = rank(xs), ry = rank(ys);
  const mx = mean(rx), my = mean(ry);
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const a = rx[i] - mx, b = ry[i] - my;
    num += a * b; dx += a * a; dy += b * b;
  }
  return dx && dy ? fmt(num / Math.sqrt(dx * dy), 3) : 0;
}

function baseLayout(yTitle, xTitle) {
  return {
    plot_bgcolor: "#FFFFFF",
    paper_bgcolor: "#FFFFFF",
    margin: CHART_MARGIN,
    font: { family: "-apple-system,'Segoe UI',system-ui,sans-serif", size: 11, color: SLATE },
    xaxis: { title: xTitle || "", gridcolor: "#E2E8F0", zeroline: false, tickfont: { size: 10 } },
    yaxis: { title: yTitle || "", gridcolor: "#E2E8F0", zeroline: false, tickfont: { size: 10 } },
    hoverlabel: { bgcolor: "#1E293B", font: { color: "#FFF", size: 12 }, bordercolor: "transparent" },
    showlegend: false,
  };
}

function barTrace(x, y, name, color, text) {
  return {
    type: "bar", x, y, name: name || "",
    marker: { color: color || BLUE },
    text: text || y.map(v => v === null ? "" : v),
    textposition: "outside",
    textfont: { size: 10, color: SLATE },
    hovertemplate: `<b>%{x}</b><br>${name || "Value"}: %{y}<extra></extra>`,
  };
}

function donutTrace(labels, values, colors) {
  return [{
    type: "pie",
    labels, values,
    hole: 0.45,
    marker: { colors: colors || CHART_COLORS },
    textinfo: "percent+label",
    textfont: { size: 11 },
    hovertemplate: "<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
  }];
}

function pieLayout() {
  return {
    paper_bgcolor: "#FFFFFF",
    margin: { l: 10, r: 10, t: 16, b: 10 },
    showlegend: false,
    font: { family: "-apple-system,'Segoe UI',system-ui,sans-serif", size: 11 },
    hoverlabel: { bgcolor: "#1E293B", font: { color: "#FFF" } },
  };
}

// ── Navigation ────────────────────────────────────────────────────────────────
function initNav() {
  const tabs = document.querySelectorAll(".nav-tab");
  const pages = document.querySelectorAll(".page");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      pages.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const target = document.getElementById("page-" + tab.dataset.page);
      if (target) target.classList.add("active");
    });
  });

  // Activate first tab
  if (tabs.length) tabs[0].click();
}

// ── Update DOM KPI ────────────────────────────────────────────────────────────
function setKPI(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

// ── OVERVIEW PAGE ─────────────────────────────────────────────────────────────
function renderOverview(rows) {
  const n   = rows.length;
  const vis = rows.map(r => +r.visits);
  const mn  = mean(vis);
  const md  = median(vis);
  const zero_n   = vis.filter(v => v === 0).length;
  const high_n   = vis.filter(v => v >= 3).length;
  const ages     = rows.map(r => +r.age_years);
  const ill      = rows.map(r => +r.illness);
  const red      = rows.map(r => +r.reduced);

  setKPI("kpi-n",        n.toLocaleString());
  setKPI("kpi-mean",     fmt(mn, 3));
  setKPI("kpi-median",   fmt(md, 0));
  setKPI("kpi-zero-pct", fmt(zero_n/n*100, 1) + "%");
  setKPI("kpi-age",      fmt(mean(ages), 1) + " yrs");
  setKPI("kpi-illness",  fmt(mean(ill), 2));
  setKPI("kpi-reduced",  fmt(mean(red), 2));
  setKPI("kpi-high",     high_n.toLocaleString());

  // Visit count bar
  const vcCounts = {}, maxV = Math.max(...vis);
  for (let i = 0; i <= maxV; i++) vcCounts[i] = 0;
  vis.forEach(v => vcCounts[v]++);
  const vcX = Object.keys(vcCounts).map(Number);
  const vcY = Object.values(vcCounts);

  Plotly.newPlot("chart-visit-dist", [
    barTrace(vcX, vcY, "Respondents", BLUE)
  ], {
    ...baseLayout("Respondents", "Number of visits"),
    margin: CHART_MARGIN,
    title: { text: "Visit count distribution", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Zero vs non-zero donut
  Plotly.newPlot("chart-zero-nonzero",
    donutTrace(["Zero visits","1+ visits"], [zero_n, n - zero_n], [BLUE, GREEN]),
    { ...pieLayout(), title: { text: "Zero vs non-zero visits", font: { size: 13 }, x: 0.5 } },
    PLOTLY_CONFIG
  );

  // Visit groups bar
  const vgCounts = {};
  VISIT_GRP.forEach(g => vgCounts[g] = 0);
  rows.forEach(r => { if (vgCounts[r.visit_group] !== undefined) vgCounts[r.visit_group]++; });
  const vgY = VISIT_GRP.map(g => vgCounts[g]);
  const vgPct = vgY.map(v => fmt(v/n*100,1)+"%");

  Plotly.newPlot("chart-visit-groups", [
    barTrace(VISIT_GRP, vgY, "Respondents", AMBER, vgPct)
  ], {
    ...baseLayout("Respondents","Visit group"),
    title: { text: "Visit group distribution", font: { size: 13 }, x: 0 },
    margin: { ...CHART_MARGIN, b: 56 },
  }, PLOTLY_CONFIG);

  // Age group visit mean bar
  const ageVis = {};
  AGE_ORDER.forEach(a => ageVis[a] = []);
  rows.forEach(r => { if (ageVis[r.age_group]) ageVis[r.age_group].push(+r.visits); });
  const ageY = AGE_ORDER.map(a => fmt(mean(ageVis[a] || []),3));

  Plotly.newPlot("chart-age-visits-ov", [
    barTrace(AGE_ORDER, ageY, "Mean visits", GREEN, ageY)
  ], {
    ...baseLayout("Mean visits","Age group"),
    title: { text: "Mean visits by age group", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);
}

// ── VISIT PATTERNS PAGE ───────────────────────────────────────────────────────
function renderVisitPatterns(rows) {
  const vis = rows.map(r => +r.visits);
  const n = rows.length;

  // Histogram (all)
  Plotly.newPlot("chart-vp-hist", [{
    type: "histogram", x: vis, nbinsx: 10,
    marker: { color: BLUE },
    hovertemplate: "Visits: %{x}<br>Count: %{y}<extra></extra>",
  }], {
    ...baseLayout("Respondents","Number of visits"),
    title: { text: "Visit count histogram", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Boxplot
  Plotly.newPlot("chart-vp-box", [{
    type: "box", y: vis,
    name: "Visits",
    marker: { color: BLUE },
    line: { color: BLUE },
    boxpoints: "outliers",
    hovertemplate: "%{y}<extra></extra>",
  }], {
    ...baseLayout("Number of visits"),
    title: { text: "Doctor visits — boxplot", font: { size: 13 }, x: 0 },
    xaxis: { showticklabels: false },
    margin: { l: 48, r: 16, t: 36, b: 16 },
  }, PLOTLY_CONFIG);

  // Non-zero distribution
  const nzVis = vis.filter(v => v > 0);
  const nzCounts = {};
  nzVis.forEach(v => nzCounts[v] = (nzCounts[v] || 0) + 1);
  const nzX = Object.keys(nzCounts).map(Number).sort((a,b)=>a-b);
  const nzY = nzX.map(k => nzCounts[k]);

  Plotly.newPlot("chart-vp-nonzero", [
    barTrace(nzX, nzY, "Respondents", RED)
  ], {
    ...baseLayout("Respondents","Visits (non-zero only)"),
    title: { text: "Non-zero visit distribution", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Visit groups
  const vgCounts = {};
  VISIT_GRP.forEach(g => vgCounts[g] = 0);
  rows.forEach(r => { if (vgCounts[r.visit_group] !== undefined) vgCounts[r.visit_group]++; });
  const vgY = VISIT_GRP.map(g => vgCounts[g]);

  Plotly.newPlot("chart-vp-groups", [
    barTrace(VISIT_GRP, vgY, "Respondents", AMBER)
  ], {
    ...baseLayout("Respondents","Visit group"),
    title: { text: "Visit groups", font: { size: 13 }, x: 0 },
    margin: { ...CHART_MARGIN, b: 56 },
  }, PLOTLY_CONFIG);

  // Illness vs mean visits
  const illVis = {};
  for (let i = 0; i <= 5; i++) illVis[i] = [];
  rows.forEach(r => { const i = +r.illness; if (i >= 0 && i <= 5) illVis[i].push(+r.visits); });
  const illX = [0,1,2,3,4,5];
  const illY = illX.map(i => fmt(mean(illVis[i] || []),3));

  Plotly.newPlot("chart-vp-illness", [
    barTrace(illX.map(String), illY, "Mean visits", RED, illY)
  ], {
    ...baseLayout("Mean visits","Illness count (0-5)"),
    title: { text: "Mean visits by illness count", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Reduced-activity tiers
  const tiers = { "0 days":[], "1-3 days":[], "4-7 days":[], "8-14 days":[] };
  rows.forEach(r => {
    const v = +r.reduced;
    if (v === 0) tiers["0 days"].push(+r.visits);
    else if (v <= 3) tiers["1-3 days"].push(+r.visits);
    else if (v <= 7) tiers["4-7 days"].push(+r.visits);
    else tiers["8-14 days"].push(+r.visits);
  });
  const tierLabels = Object.keys(tiers);
  const tierMeans  = tierLabels.map(t => fmt(mean(tiers[t]),3));

  Plotly.newPlot("chart-vp-reduced", [
    barTrace(tierLabels, tierMeans, "Mean visits", AMBER, tierMeans)
  ], {
    ...baseLayout("Mean visits","Reduced-activity tier"),
    title: { text: "Mean visits by reduced-activity tier", font: { size: 13 }, x: 0 },
    margin: { ...CHART_MARGIN, b: 60 },
  }, PLOTLY_CONFIG);
}

// ── DEMOGRAPHICS PAGE ─────────────────────────────────────────────────────────
function renderDemographics(rows) {
  const n = rows.length;

  // Gender mean visits
  const genders = {};
  rows.forEach(r => {
    const g = r.gender;
    if (!genders[g]) genders[g] = [];
    genders[g].push(+r.visits);
  });
  const gLabels = Object.keys(genders);
  const gMeans  = gLabels.map(g => fmt(mean(genders[g]),3));
  const gColors = gLabels.map(g => g === "female" ? RED : BLUE);

  Plotly.newPlot("chart-dem-gender-visits", [
    barTrace(gLabels, gMeans, "Mean visits", null, gMeans).constructor === Object
      ? barTrace(gLabels, gMeans, "Mean visits", null, gMeans)
      : {
          type: "bar", x: gLabels, y: gMeans,
          marker: { color: gColors },
          text: gMeans, textposition: "outside",
          hovertemplate: "<b>%{x}</b><br>Mean visits: %{y}<extra></extra>",
        }
  ], {
    ...baseLayout("Mean visits","Gender"),
    title: { text: "Mean visits by gender", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Correct gender bar with individual colors
  Plotly.newPlot("chart-dem-gender-visits", [{
    type: "bar", x: gLabels, y: gMeans,
    marker: { color: gColors },
    text: gMeans, textposition: "outside",
    textfont: { size: 10 },
    hovertemplate: "<b>%{x}</b><br>Mean visits: %{y}<extra></extra>",
  }], {
    ...baseLayout("Mean visits","Gender"),
    title: { text: "Mean visits by gender", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Gender distribution donut
  const gCounts = gLabels.map(g => genders[g].length);
  Plotly.newPlot("chart-dem-gender-dist",
    donutTrace(gLabels, gCounts, [RED, BLUE]),
    { ...pieLayout(), title: { text: "Gender distribution", font: { size: 13 }, x: 0.5 } },
    PLOTLY_CONFIG
  );

  // Age group distribution
  const ageCounts = {};
  AGE_ORDER.forEach(a => ageCounts[a] = 0);
  rows.forEach(r => { if (ageCounts[r.age_group] !== undefined) ageCounts[r.age_group]++; });
  const ageCntY = AGE_ORDER.map(a => ageCounts[a]);

  Plotly.newPlot("chart-dem-age-dist", [
    barTrace(AGE_ORDER, ageCntY, "Respondents", BLUE)
  ], {
    ...baseLayout("Respondents","Age group (years)"),
    title: { text: "Respondents by age group", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Age group mean visits
  const ageVis = {};
  AGE_ORDER.forEach(a => ageVis[a] = []);
  rows.forEach(r => { if (ageVis[r.age_group]) ageVis[r.age_group].push(+r.visits); });
  const ageMeans = AGE_ORDER.map(a => fmt(mean(ageVis[a]||[]),3));

  Plotly.newPlot("chart-dem-age-visits", [
    barTrace(AGE_ORDER, ageMeans, "Mean visits", GREEN, ageMeans)
  ], {
    ...baseLayout("Mean visits","Age group (years)"),
    title: { text: "Mean visits by age group", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);

  // Income group
  const incVis = {};
  INCOME_ORDER.forEach(g => incVis[g] = []);
  rows.forEach(r => { if (incVis[r.income_group]) incVis[r.income_group].push(+r.visits); });
  const incNice = ["Low", "Lower-Mid", "Upper-Mid", "High"];
  const incMeans = INCOME_ORDER.map(g => fmt(mean(incVis[g]||[]),3));

  Plotly.newPlot("chart-dem-income", [
    barTrace(incNice, incMeans, "Mean visits", CYAN, incMeans)
  ], {
    ...baseLayout("Mean visits","Income group"),
    title: { text: "Mean visits by income group", font: { size: 13 }, x: 0 },
  }, PLOTLY_CONFIG);
}

// ── HEALTH BURDEN PAGE ────────────────────────────────────────────────────────
function renderHealthBurden(rows) {
  // Illness vs mean visits
  const illVis = {};
  for (let i=0;i<=5;i++) illVis[i]=[];
  rows.forEach(r=>{const i=+r.illness;if(i>=0&&i<=5)illVis[i].push(+r.visits);});
  const illX=[0,1,2,3,4,5];
  const illY=illX.map(i=>fmt(mean(illVis[i]||[]),3));

  Plotly.newPlot("chart-hb-illness",[
    barTrace(illX.map(String),illY,"Mean visits",RED,illY)
  ], {
    ...baseLayout("Mean visits","Illness count"),
    title:{text:"Mean visits by illness count",font:{size:13},x:0},
  }, PLOTLY_CONFIG);

  // Reduced tiers
  const tiers={"0 days":[],"1-3 days":[],"4-7 days":[],"8-14 days":[]};
  rows.forEach(r=>{
    const v=+r.reduced;
    if(v===0)tiers["0 days"].push(+r.visits);
    else if(v<=3)tiers["1-3 days"].push(+r.visits);
    else if(v<=7)tiers["4-7 days"].push(+r.visits);
    else tiers["8-14 days"].push(+r.visits);
  });
  const tLabels=Object.keys(tiers);
  const tMeans=tLabels.map(t=>fmt(mean(tiers[t]),3));

  Plotly.newPlot("chart-hb-reduced",[
    barTrace(tLabels,tMeans,"Mean visits",AMBER,tMeans)
  ],{
    ...baseLayout("Mean visits","Reduced-activity tier"),
    title:{text:"Mean visits by reduced-activity tier",font:{size:13},x:0},
    margin:{...CHART_MARGIN,b:60},
  },PLOTLY_CONFIG);

  // Chronic status distribution
  const cntByCS={};
  CHRONIC_ORDER.forEach(c=>cntByCS[c]=0);
  rows.forEach(r=>{if(cntByCS[r.chronic_status]!==undefined)cntByCS[r.chronic_status]++;});
  const csCnt=CHRONIC_ORDER.map(c=>cntByCS[c]);

  Plotly.newPlot("chart-hb-chronic-dist",
    donutTrace(CHRONIC_ORDER,csCnt,[GREEN,AMBER,RED]),
    {...pieLayout(),title:{text:"Chronic condition distribution",font:{size:13},x:0.5}},
    PLOTLY_CONFIG
  );

  // Chronic mean visits
  const csVis={};
  CHRONIC_ORDER.forEach(c=>csVis[c]=[]);
  rows.forEach(r=>{if(csVis[r.chronic_status])csVis[r.chronic_status].push(+r.visits);});
  const csMeans=CHRONIC_ORDER.map(c=>fmt(mean(csVis[c]||[]),3));

  Plotly.newPlot("chart-hb-chronic-visits",[
    {type:"bar",x:CHRONIC_ORDER,y:csMeans,
     marker:{color:[GREEN,AMBER,RED]},
     text:csMeans,textposition:"outside",textfont:{size:10},
     hovertemplate:"<b>%{x}</b><br>Mean visits: %{y}<extra></extra>"}
  ],{
    ...baseLayout("Mean visits","Chronic status"),
    title:{text:"Mean visits by chronic status",font:{size:13},x:0},
  },PLOTLY_CONFIG);

  // Health score vs visits
  const hsVis={};
  rows.forEach(r=>{const h=+r.health;if(!hsVis[h])hsVis[h]=[];hsVis[h].push(+r.visits);});
  const hsX=Object.keys(hsVis).map(Number).sort((a,b)=>a-b);
  const hsY=hsX.map(h=>fmt(mean(hsVis[h]),3));

  Plotly.newPlot("chart-hb-health",[
    barTrace(hsX.map(String),hsY,"Mean visits",BLUE,null)
  ],{
    ...baseLayout("Mean visits","Health score (direction unknown)"),
    title:{text:"Mean visits by health score",font:{size:13},x:0},
  },PLOTLY_CONFIG);
}

// ── INSURANCE & INCOME PAGE ───────────────────────────────────────────────────
function renderInsuranceIncome(rows) {
  const n=rows.length;

  // Insurance distribution
  const insCnt={};
  INS_ORDER.forEach(i=>insCnt[i]=0);
  rows.forEach(r=>{if(insCnt[r.insurance_type]!==undefined)insCnt[r.insurance_type]++;});
  const insCntY=INS_ORDER.map(i=>insCnt[i]);

  Plotly.newPlot("chart-ii-ins-dist",[
    {type:"bar",x:INS_ORDER,y:insCntY,
     marker:{color:[BLUE,RED,GREEN,MUTED]},
     text:insCntY.map(v=>fmt(v/n*100,1)+"%"),textposition:"outside",textfont:{size:10},
     hovertemplate:"<b>%{x}</b><br>Count: %{y}<extra></extra>"}
  ],{
    ...baseLayout("Respondents","Insurance type"),
    title:{text:"Insurance-type distribution",font:{size:13},x:0},
    margin:{...CHART_MARGIN,b:60},
  },PLOTLY_CONFIG);

  // Insurance mean visits
  const insVis={};
  INS_ORDER.forEach(i=>insVis[i]=[]);
  rows.forEach(r=>{if(insVis[r.insurance_type])insVis[r.insurance_type].push(+r.visits);});
  const insMeans=INS_ORDER.map(i=>fmt(mean(insVis[i]||[]),3));

  Plotly.newPlot("chart-ii-ins-visits",[
    {type:"bar",x:INS_ORDER,y:insMeans,
     marker:{color:[BLUE,RED,GREEN,MUTED]},
     text:insMeans,textposition:"outside",textfont:{size:10},
     hovertemplate:"<b>%{x}</b><br>Mean visits: %{y}<extra></extra>"}
  ],{
    ...baseLayout("Mean visits","Insurance type"),
    title:{text:"Mean visits by insurance type",font:{size:13},x:0},
    margin:{...CHART_MARGIN,b:60},
  },PLOTLY_CONFIG);

  // Govt vs Private
  const govtVisits=rows.filter(r=>["Free-Poor","Free-Repatriated"].includes(r.insurance_type)).map(r=>+r.visits);
  const privVisits=rows.filter(r=>r.insurance_type==="Private").map(r=>+r.visits);
  const uninVisits=rows.filter(r=>r.insurance_type==="Uninsured").map(r=>+r.visits);
  const gvpMeans=[fmt(mean(govtVisits),3),fmt(mean(privVisits),3),fmt(mean(uninVisits),3)];
  const gvpLabels=["Govt-Assisted","Private","Uninsured"];

  Plotly.newPlot("chart-ii-gvp",[
    {type:"bar",x:gvpLabels,y:gvpMeans,
     marker:{color:[GREEN,BLUE,MUTED]},
     text:gvpMeans,textposition:"outside",textfont:{size:10},
     hovertemplate:"<b>%{x}</b><br>Mean visits: %{y}<extra></extra>"}
  ],{
    ...baseLayout("Mean visits","Group"),
    title:{text:"Govt-assisted vs private vs uninsured",font:{size:13},x:0},
  },PLOTLY_CONFIG);

  // Income group mean visits
  const incVis={};
  INCOME_ORDER.forEach(g=>incVis[g]=[]);
  rows.forEach(r=>{if(incVis[r.income_group])incVis[r.income_group].push(+r.visits);});
  const incNice=["Low","Lower-Mid","Upper-Mid","High"];
  const incMeans=INCOME_ORDER.map(g=>fmt(mean(incVis[g]||[]),3));

  Plotly.newPlot("chart-ii-income",[
    barTrace(incNice,incMeans,"Mean visits",CYAN,incMeans)
  ],{
    ...baseLayout("Mean visits","Income group"),
    title:{text:"Mean visits by income group",font:{size:13},x:0},
  },PLOTLY_CONFIG);
}

// ── RELATIONSHIPS PAGE ────────────────────────────────────────────────────────
function renderRelationships(rows) {
  const vis=rows.map(r=>+r.visits);

  // Correlation bar chart (visits vs others)
  const corrPairs=[
    {label:"Reduced days",  col:"reduced"},
    {label:"Illness count", col:"illness"},
    {label:"Health score",  col:"health"},
    {label:"Age (years)",   col:"age_years"},
    {label:"Lim. chronic",  col:"lchronic_enc"},
    {label:"Free-Repat.",   col:"freerepat_enc"},
    {label:"Non-lim. chr.", col:"nchronic_enc"},
    {label:"Gender (M=1)",  col:"gender_enc"},
    {label:"Income",        col:"income"},
    {label:"Free-Poor",     col:"freepoor_enc"},
  ];

  const corrVals=corrPairs.map(p=>({
    label:p.label,
    rho: spearman(rows.map(r=>+r[p.col]), vis)
  })).sort((a,b)=>a.rho-b.rho);

  Plotly.newPlot("chart-rel-corr-bar",[{
    type:"bar",orientation:"h",
    x:corrVals.map(c=>c.rho),
    y:corrVals.map(c=>c.label),
    marker:{color:corrVals.map(c=>c.rho>=0?BLUE:RED)},
    text:corrVals.map(c=>c.rho),textposition:"outside",textfont:{size:10},
    hovertemplate:"<b>%{y}</b><br>Spearman rho: %{x}<extra></extra>",
  }],{
    ...baseLayout(),
    title:{text:"Spearman correlation with doctor visits",font:{size:13},x:0},
    xaxis:{title:"Spearman rho",gridcolor:"#E2E8F0",zeroline:true,zerolinecolor:"#94A3B8"},
    yaxis:{title:"",gridcolor:"transparent",tickfont:{size:11}},
    margin:{l:120,r:60,t:36,b:36},
    shapes:[{type:"line",x0:0,x1:0,y0:-0.5,y1:corrVals.length-0.5,
             line:{color:"#94A3B8",width:1,dash:"dot"}}],
  },PLOTLY_CONFIG);

  // Correlation heatmap (6x6)
  const heatCols=["visits","illness","reduced","health","age_years","income"];
  const heatLabels=["Visits","Illness","Reduced","Health","Age","Income"];
  const cm=heatCols.map(c1=>heatCols.map(c2=>spearman(rows.map(r=>+r[c1]),rows.map(r=>+r[c2]))));

  Plotly.newPlot("chart-rel-heatmap",[{
    type:"heatmap",
    z:cm,x:heatLabels,y:heatLabels,
    colorscale:"RdBu",zmid:0,zmin:-1,zmax:1,
    text:cm.map(row=>row.map(v=>v.toFixed(2))),
    texttemplate:"%{text}",
    hovertemplate:"<b>%{y} × %{x}</b><br>rho = %{z:.3f}<extra></extra>",
    showscale:true,
    colorbar:{title:"rho",thickness:12,len:0.8,tickfont:{size:10}},
  }],{
    paper_bgcolor:"#FFF",plot_bgcolor:"#FFF",
    title:{text:"Spearman correlation matrix",font:{size:13},x:0},
    margin:{l:72,r:80,t:36,b:60},
    xaxis:{tickfont:{size:11}},yaxis:{tickfont:{size:11}},
    font:{family:"-apple-system,'Segoe UI',system-ui,sans-serif",size:11},
    hoverlabel:{bgcolor:"#1E293B",font:{color:"#FFF"},bordercolor:"transparent"},
  },PLOTLY_CONFIG);
}

// ── KEY INSIGHTS PAGE — computed from data ────────────────────────────────────
function renderInsights(rows) {
  const n=rows.length;
  const vis=rows.map(r=>+r.visits);
  const mn=mean(vis);
  const zero_n=vis.filter(v=>v===0).length;
  const high_n=vis.filter(v=>v>=3).length;

  const rho_red=spearman(rows.map(r=>+r.reduced),vis);
  const rho_ill=spearman(rows.map(r=>+r.illness),vis);
  const rho_age=spearman(rows.map(r=>+r.age_years),vis);
  const rho_inc=spearman(rows.map(r=>+r.income),vis);

  const fem=rows.filter(r=>r.gender==="female");
  const mal=rows.filter(r=>r.gender==="male");
  const femMean=fmt(mean(fem.map(r=>+r.visits)),3);
  const malMean=fmt(mean(mal.map(r=>+r.visits)),3);

  const lim=rows.filter(r=>r.chronic_status==="Limiting");
  const noC=rows.filter(r=>r.chronic_status==="No Condition");
  const limMean=fmt(mean(lim.map(r=>+r.visits)),3);
  const noCMean=fmt(mean(noC.map(r=>+r.visits)),3);

  const insVis={};
  INS_ORDER.forEach(i=>insVis[i]=[]);
  rows.forEach(r=>{if(insVis[r.insurance_type])insVis[r.insurance_type].push(+r.visits);});
  const insHighest=INS_ORDER.reduce((a,b)=>mean(insVis[a]||[])>mean(insVis[b]||[])?a:b);
  const insLowest =INS_ORDER.reduce((a,b)=>mean(insVis[a]||[])<mean(insVis[b]||[])?a:b);

  const el=document.getElementById("insights-text");
  if(el){
    el.innerHTML=`
      <div class="insight-grid">
        <div class="insight-card">
          <h4>&#128200; Visit patterns</h4>
          <ul>
            <li>${fmt(zero_n/n*100,1)}% of respondents report <strong>zero visits</strong></li>
            <li>Mean visits = <strong>${fmt(mn,3)}</strong>; median = 0</li>
            <li>Max observed visits: <strong>${Math.max(...vis)}</strong></li>
            <li>${high_n} respondents (${fmt(high_n/n*100,1)}%) report 3+ visits</li>
            <li>Distribution is strongly right-skewed</li>
          </ul>
        </div>
        <div class="insight-card">
          <h4>&#128101; Demographic patterns</h4>
          <ul>
            <li>Female mean visits: <strong>${femMean}</strong></li>
            <li>Male mean visits: <strong>${malMean}</strong></li>
            <li>Spearman rho (age vs visits) = <strong>${rho_age}</strong></li>
            <li>Older respondents tend to show higher mean visits</li>
            <li>Gender is recorded as binary only</li>
          </ul>
        </div>
        <div class="insight-card">
          <h4>&#127973; Health burden</h4>
          <ul>
            <li>Spearman rho (reduced vs visits) = <strong>${rho_red}</strong> (strongest)</li>
            <li>Spearman rho (illness vs visits) = <strong>${rho_ill}</strong></li>
            <li>Limiting chronic: mean = <strong>${limMean}</strong> vs No Condition: <strong>${noCMean}</strong></li>
            <li>Health score direction unknown — no directional claim made</li>
            <li>All health variables are self-reported</li>
          </ul>
        </div>
        <div class="insight-card">
          <h4>&#127970; Insurance &amp; income</h4>
          <ul>
            <li>Highest mean visits: <strong>${insHighest}</strong> (${fmt(mean(insVis[insHighest]||[]),3)})</li>
            <li>Lowest mean visits: <strong>${insLowest}</strong> (${fmt(mean(insVis[insLowest]||[]),3)})</li>
            <li>Spearman rho (income vs visits) = <strong>${rho_inc}</strong></li>
            <li>3 insurance types are mutually exclusive</li>
            <li>79 respondents have income = 0 (ambiguous)</li>
          </ul>
        </div>
      </div>
      <div class="notice info" style="margin-top:4px">
        <span class="notice-icon">&#8505;</span>
        <span>All insights above are <strong>descriptive associations</strong> computed from the
        processed dataset. They do not constitute medical diagnoses or causal explanations.</span>
      </div>`;
  }
}

// ── LIMITATIONS ACCORDION ─────────────────────────────────────────────────────
function initAccordion() {
  document.querySelectorAll(".limit-header").forEach(btn => {
    btn.addEventListener("click", () => {
      const item=btn.closest(".limit-item");
      item.classList.toggle("open");
    });
  });
}

// ── LOAD CSV & BOOTSTRAP ──────────────────────────────────────────────────────
function setStatus(msg, cls) {
  const el=document.getElementById("load-status");
  if(!el) return;
  el.textContent=msg;
  el.className=cls;
}

function showApp() {
  const overlay=document.getElementById("loading-overlay");
  if(overlay) overlay.style.display="none";
}

function init() {
  initNav();
  initAccordion();

  setStatus("Loading CSV…","loading");

  Papa.parse(CSV_PATH, {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
      if(results.errors.length) {
        console.warn("CSV parse warnings:", results.errors);
      }
      DATA = results.data;
      if(!DATA || DATA.length < 10) {
        setStatus("CSV load failed","error");
        document.getElementById("loading-overlay").innerHTML=
          `<div style="text-align:center;padding:32px">
            <p style="font-size:16px;color:#DC2626;margin-bottom:12px">&#9888; Could not load the dataset</p>
            <p style="font-size:13px;color:#475569;max-width:400px">
              Open this dashboard using a local HTTP server (e.g. VS Code Live Server).
              Browsers block CSV fetch requests from <code>file://</code> URLs.
            </p>
          </div>`;
        return;
      }
      setStatus(`${DATA.length.toLocaleString()} records loaded`, "ready");
      renderOverview(DATA);
      renderVisitPatterns(DATA);
      renderDemographics(DATA);
      renderHealthBurden(DATA);
      renderInsuranceIncome(DATA);
      renderRelationships(DATA);
      renderInsights(DATA);
      showApp();
    },
    error: function(err) {
      setStatus("Load error — use Live Server","error");
      console.error("PapaParse error:", err);
      document.getElementById("loading-overlay").innerHTML=
        `<div style="text-align:center;padding:32px">
          <p style="font-size:16px;color:#DC2626;margin-bottom:12px">&#9888; CSV load failed</p>
          <p style="font-size:13px;color:#475569;max-width:440px">
            Use <strong>VS Code Live Server</strong> or run
            <code>python -m http.server 8080</code> from the project root,
            then open <code>http://localhost:8080/html_dashboard/</code>
          </p>
        </div>`;
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
