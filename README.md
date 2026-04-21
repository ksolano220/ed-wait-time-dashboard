## Emergency Department Wait Times Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ksolano220-ed-wait-times.streamlit.app/)

Interactive Streamlit dashboard analyzing ED wait times across **4,000+ US hospitals** using CMS Timely and Effective Care data.

### Live Demo

[ksolano220-ed-wait-times.streamlit.app](https://ksolano220-ed-wait-times.streamlit.app/)

### Features
- **Choropleth map** of median wait times by state
- **Filters** by state, ED volume, and wait time range
- **Box plots** comparing wait times across low/medium/high/very high volume EDs
- **Scatter plot** showing the relationship between wait time and left-before-seen rates
- **State ranking** bar chart
- **Hospital detail tables** for longest and shortest waits

### Data Source
[CMS Timely and Effective Care: Hospital](https://data.cms.gov/provider-data/dataset/yv7e-xc69) (2024–2025 reporting period)

Key measures:
| Measure | Description |
|---------|-------------|
| OP-18b | Median time patients spent in ED before leaving (discharged patients) |
| OP-22 | Percentage of patients who left before being seen |
| EDV | Emergency department volume category |

### How to Run

```bash
pip install -r requirements.txt

# Download CMS data
python src/download_data.py

# Prepare hospital-level dataset
python src/prepare_data.py

# Launch dashboard
streamlit run app.py
```

### Key Findings
- National median ED wait is **148 minutes** (nearly 2.5 hours). Baseline is already bad enough that half of US EDs would fail most private-market SLAs.
- **High-volume EDs have significantly longer waits** than low-volume facilities. Throughput bottlenecks are structural, not just peak-hour spikes, which suggests capacity and staffing ratios are the lever, not triage workflow.
- Wait time correlates with **left-before-seen (LBS) rates**. Longer waits mean more patients leave without care. LBS is a useful proxy for unmet demand and a revenue loss signal for administrators.
- **MD, DC, and NJ consistently rank among the longest waits.** Wait-time leaders cluster around the dense Northeast corridor, which suggests capacity investment is lagging population density in those markets.

### Tools Used
- Python, Streamlit, Plotly, pandas
- CMS public hospital data
