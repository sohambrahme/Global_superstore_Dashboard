# Commercial Retail Intelligence System

## Business Problem
Global Superstore requires a professional-grade analytics platform to monitor commercial performance, evaluate discount elasticity, segment customers, track supply chain efficiency, and forecast future revenue. The previous reporting solution lacked advanced analytical depth and scenario planning capabilities.

## Technical Stack
- **Languages:** Python 3, SQL
- **Database:** SQLite (Star Schema Architecture)
- **Data Processing:** Pandas
- **Visualization:** Plotly
- **Machine Learning / Forecasting:** Facebook Prophet (Time-series)
- **Frontend / Application:** Streamlit (Multi-page configuration)

## Skills Demonstrated
This project is built to demonstrate core Data Analyst capabilities required in the UK commercial sector:
- **SQL & Data Modeling:** Translating a flat CSV into a Star Schema (Fact and Dimension tables) using an ETL pipeline, and utilizing SQL for KPI extraction.
- **Commercial BI & Visualization:** Developing a clean, executive-level dashboard with a corporate colour palette, steering clear of visual clutter.
- **Advanced Analytics:** Implementing RFM (Recency, Frequency, Monetary) segmentation for targeted CRM strategy.
- **Forecasting & Scenario Simulation:** Utilizing `prophet` for time-series forecasting and building a "What-if" margin simulator to present the bottom-line impact of discount elasticity.
- **Stakeholder Communication:** Providing plain-English "Commercial Insights" dynamically on every page.

## KPI Definitions
- **Profit Margin:** `(Total Profit / Total Sales) * 100`. Demonstrates absolute profitability percentage.
- **Avg Order Value (AOV):** `Total Sales / Total Orders`. The average revenue generated per checkout.
- **Shipping Days:** The difference in days between `Order Date` and `Ship Date`. A measure of operational SLA adherence.
- **MAPE (Mean Absolute Percentage Error):** The accuracy metric for the time-series forecast, calculated via a 3-month holdout backtest.

---

## Deployment Instructions

### Local Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sohambrahme/Global_superstore_Dashboard.git
   cd Global_superstore_Dashboard
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the ETL Pipeline:**
   This generates the SQLite data warehouse (`data/retail_warehouse.db`) from the source CSV.
   ```bash
   python utils/etl.py
   ```

4. **Launch the Application:**
   ```bash
   streamlit run app.py
   ```

### Cloud Deployment (Streamlit Community Cloud)
1. Fork or push this repository to your GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub account and select this repository.
4. Set the main file path to `app.py`.
5. *Note: Ensure that you've run the ETL script and committed the `data/retail_warehouse.db` file to your repo if the cloud environment does not allow write-access to run the ETL on boot.*

---
*Created as a commercial portfolio piece.*
