# TSE-diversification-analyzer
A Streamlit app to analyze portfolio diversification effects using real-time Tehran Stock Exchange (TSE) data
# 📊 TSE Diversification Analyzer

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TSE](https://img.shields.io/badge/TSE-Tehran_Stock_Exchange-green?style=for-the-badge)](http://tse.ir/)

This project is an interactive web application that leverages real-time data from the **Tehran Stock Exchange (TSE)** to visually and statistically analyze the concept of **Portfolio Diversification**.

It helps investors and analysts understand how increasing the number of assets in a portfolio can significantly reduce unsystematic risk.

---

## ✨ Key Features

- **📥 Real-time Data Fetching:** Direct connection to the TSE core via the `finpy_tse` library.
- **📅 Jalali Calendar Support:** Automatic conversion of Persian (Jalali) dates to Gregorian for time-series processing.
- **🧮 Monte Carlo Simulation:** Calculates risk for random portfolios using high-iteration sampling for accuracy.
- **📈 Interactive Visualization:** Dynamic charts powered by `Plotly` to visualize the risk reduction curve.
- **⚡ Smart Data Handling:** Includes caching to prevent redundant data downloads and robust error handling for missing market data.

---

## 🚀 Installation & Usage

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/TSE-Diversification-Analyzer.git
cd TSE-Diversification-Analyzer

### 2. Create a Virtual Environment (Recommended)
bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

### 3. Install Dependencies
bash
pip install -r requirements.txt

### 4. Run the Application
bash
streamlit run app.py

---

## 🛠️ How It Works (Technical Insight)

The application operates in three main stages:

1.  **Data Fetching & Cleaning:** 
It takes a list of TSE tickers (e.g., 'فولاد', 'فملی'), fetches their adjusted price history, and cleans the data. Since TSE data often contains gaps or stops, a robust filling method (Forward Fill) and date conversion logic are applied.

2.  **Portfolio Simulation:**
*   The app iterates through portfolio sizes ranging from `n=1` to `n=20`.
*   For each size, it generates hundreds of random portfolios and calculates the average annualized risk (Standard Deviation).

3.  **Visualization:** 
The results are plotted to show the "Diversification Curve," demonstrating how risk drops rapidly initially and then asymptotes towards **Systematic Risk**.

---

## 📸 Parameters

You can customize the analysis using the sidebar:
*   **Stock Tickers:** Enter Persian ticker names (space-separated).
*   **Start Year:** Select the starting year for historical data (Jalali year).
*   **Simulation Iterations:** Adjust the number of Monte Carlo simulations for precision.
*   **Max Portfolio Size:** Limit the x-axis of the analysis.

> **Note:** The orange dotted line in the chart represents the Systematic Market Risk, which cannot be eliminated through diversification.

---

## 📦 Libraries Used

*   `streamlit`: For the web interface.
*   `finpy_tse`: For fetching data from Tehran Stock Exchange.
*   `pandas` & `numpy`: For data manipulation and statistical calculations.
*   `plotly`: For interactive graphing.
*   `jdatetime`: For handling Persian dates.

---

## ⚠️ Disclaimer

This tool is for educational and analytical purposes only. It does not constitute financial advice or a recommendation to buy or sell any assets. Market data may be subject to delays or inaccuracies.

---

### 🤝 Contribution
Contributions are welcome! If you have ideas for better algorithms or UI improvements, feel free to open a Pull Request.

Built with ❤️ and ☕ for the financial community.

