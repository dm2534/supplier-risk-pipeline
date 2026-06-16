# Supplier Risk Scoring Pipeline

A LangChain + Gemini pipeline that monitors live news for automotive suppliers, scores each one for supply chain risk using a structured LLM output, and generates a ranked risk report with high-risk alerts.

Built as part of trial LangGraph project — simulating the kind of supply chain disruption monitoring a Tier-1 automotive manufacturer runs continuously.

---

## What it does

1. Fetches the 5 most recent news articles per supplier from NewsAPI
2. Passes articles to an LLM via a structured LangChain chain
3. Returns a typed risk assessment: score (1–10), reasoning, and risk factors
4. Ranks all suppliers by risk score and flags any scoring 7 or above as high-risk

---

## Sample Output

```
# Supplier Risk Report — June 2026

## ⚠️ HIGH RISK SUPPLIERS (Action Required)
- **Samsung SDI**: Score 5 - Samsung SDI appears strategically important and commercially active with major automaker wins, but project delays and dependence on large EV programs create moderate supply and execution risk.
- **BASF**: Score 5 - BASF shows strategic growth and large-scale investment momentum, but the articles also point to environmental liability exposure, regulatory scrutiny around PFAS, and macro-industrial weakness in Germany that could affect operational resilience.


---

| Supplier          | Risk Score | Risk Factors                              | Reasoning                                      |
|-------------------|------------|-------------------------------------------|------------------------------------------------|
| Samsung SDI       | 5/10       | Lithium shortage, EV demand surge         | Critical battery supply constraints flagged    |
| BASF              | 5/10       | Energy cost volatility, EU operations     | European energy exposure creates margin risk   |
| Aptiv             | 3/10       | Minor labour dispute Q1                   | Isolated incident, no systemic risk detected   |
| Bosch             | 1/10       | Semiconductor lead times                  | Manageable exposure, diversified supply base   |
| Magna             | 2/10       | None significant                          | Strong financials, stable operations           |
```

---

## Architecture

```
suppliers list
      ↓
fetch_supplier_news()     ← NewsAPI, 5 articles per supplier
      ↓
score_supplier_risk()     ← LangChain chain → Gemini 1.5 Flash
      ↓                      structured output via TypedDict schema
flag_high_risk()          ← filters score >= 7, prints alert block
      ↓
build_risk_report()       ← sorts by score, renders markdown table
```

---

## Stack

| Layer | Technology |
|---|---|
| Orchestration | LangChain |
| LLM | GPT-5.4-mini/ Gemini 3.5 Flash |
| News data | NewsAPI (newsapi-python) |
| Structured output | LangChain with_structured_output + TypedDict |
| Environment | Python 3.13, uv, pyproject.toml |

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/dnm54/supplier-risk-pipeline.git
cd supplier-risk-pipeline
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key
NEWS_API_KEY=your_newsapi_key
```

Get your keys at:
- Gemini: aistudio.google.com
- NewsAPI: newsapi.org

**5. Run the pipeline**
```bash
python agent.py
```

---

## Suppliers monitored

The default supplier list covers major Tier-1 and Tier-2 suppliers:

```python
suppliers = [
    "Bosch",
    "Aptiv",
    "Magna International",
    "Samsung SDI",
    "BASF"
]
```

Edit this list in `agent.py` to monitor any supplier.

---

## Extending this project

**Add LangGraph orchestration** — refactor the three functions into a `StateGraph` with conditional edges that route high-risk suppliers to an alert node. This is the next iteration of this project.

**Add more suppliers** — the pipeline scales linearly. Add any supplier name to the list.

**Scheduled runs** — wrap in a Cloud Scheduler + Cloud Run deployment to run daily and email the report. Architecture mirrors the daily newspaper agent in this portfolio.

---

## Enterprise use case

This pipeline maps directly to supply chain risk monitoring at scale — the same pattern used by automotive manufacturers to track disruption signals across hundreds of suppliers in real time. The structured output schema (`supplier`, `score`, `reasoning`, `risk_factors`) is designed to feed downstream dashboards, alerting systems, or procurement workflows.

---

## Author

**Dale Monteiro**
GCP Professional Architect & ML Engineer
[LinkedIn](https://linkedin.com/in/dalemonteiro-90a3b4213)
