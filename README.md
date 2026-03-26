## Emergency Department Wait Times Dashboard

Interactive Streamlit dashboard analyzing ED wait times across **4,000+ US hospitals** using CMS Timely and Effective Care data.

### Features
- **Choropleth map** of median wait times by state
- **Filters** by state, ED volume, and wait time range
- **Box plots** comparing wait times across low/medium/high/very high volume EDs
- **Scatter plot** showing the relationship between wait time and left-before-seen rates
- **State ranking** bar chart
- **Hospital detail tables** for longest and shortest waits

### Data Source
[CMS Timely and Effective Care — Hospital](https://data.cms.gov/provider-data/dataset/yv7e-xc69) (2024–2025 reporting period)

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
- National median ED wait is **148 minutes** (nearly 2.5 hours)
- High-volume EDs have **significantly longer waits** than low-volume facilities
- Wait time correlates with left-before-seen rates — longer waits mean more patients leave
- Several states (MD, DC, NJ) consistently rank among the longest waits

### Tools Used
- Python, Streamlit, Plotly, pandas
- CMS public hospital data
