# Walmart Sales Forecasting

An end-to-end **Machine Learning and Time Series Forecasting** project that analyzes Walmart historical sales data, identifies trends, seasonality, and anomalies, compares multiple forecasting models, and provides business-oriented sales predictions through an interactive web dashboard.

## Project Overview

Retail sales are influenced by recurring seasonal patterns, holidays, store characteristics, and historical demand. Accurate sales forecasting can help businesses improve inventory planning, staffing, supply-chain operations, finance planning, and transportation capacity.

This project uses the **Walmart Recruiting – Store Sales Forecasting** dataset to build an end-to-end forecasting pipeline.

The project explores multiple forecasting approaches and ultimately uses **Prophet** as the final forecasting model for the dashboard.

## Key Objectives

* Analyze historical Walmart sales trends
* Identify weekly and monthly sales patterns
* Understand yearly seasonality and recurring holiday patterns
* Detect unusual sales behavior and anomalies
* Compare multiple forecasting approaches
* Evaluate models using MAE, RMSE, and WMAE
* Select a final forecasting model based on evaluation results
* Convert forecasts into business planning insights
* Provide an interactive forecasting dashboard
* Design a production-oriented monitoring and alert workflow

## Project Workflow

```text
Walmart Dataset
       ↓
Data Understanding & Cleaning
       ↓
Exploratory Data Analysis
       ↓
Trend Analysis
       ↓
Seasonality Analysis
       ↓
Anomaly Analysis
       ↓
Feature Engineering
       ↓
Multiple Forecasting Models
       ↓
Model Evaluation
       ↓
Prophet as Final Model
       ↓
Business Impact Analysis
       ↓
Interactive React Dashboard
       ↓
Forecast Monitoring & Alerts
```

## Dataset

The project uses the **Walmart Recruiting – Store Sales Forecasting** dataset from Kaggle.

Main files:

* `train.csv` — historical weekly sales
* `test.csv` — future dates for forecasting
* `features.csv` — temperature, fuel price, markdowns, CPI, unemployment, and holiday information
* `stores.csv` — store type and size information

Target variable:

```text
Weekly_Sales
```

The dataset contains **weekly observations represented by Friday dates**.

## Time Series Analysis

The historical sales data was analyzed to identify:

* Overall sales trends
* Weekly sales patterns
* Monthly sales patterns
* Yearly patterns
* Holiday effects
* Recurring seasonal behavior
* Rolling sales trends

The analysis showed particularly noticeable seasonal behavior during the **November–December holiday period**.

## Anomaly Analysis

Anomaly detection was performed to identify unusual sales behavior.

The analysis included:

* Negative sales observations
* IQR-based outlier detection
* Large deviations from rolling averages
* Holiday-related sales spikes
* Relationship between unusual sales and markdown activity

The anomalies were analyzed rather than automatically removed, since unusual or negative sales values can have different business meanings.

## Forecasting Models

Multiple forecasting approaches were implemented and compared.

### ARMA

A classical time-series model used as a forecasting baseline.

### SARMA

A seasonal extension used to model recurring seasonal behavior.

### Prophet

A modern time-series forecasting model designed to capture trend and seasonality.

**Prophet was selected as the final forecasting model used by the dashboard.**

### LSTM

A neural-network-based forecasting approach was also explored using historical sales sequences.

## Model Evaluation

The models were evaluated using:

* **MAE** — Mean Absolute Error
* **RMSE** — Root Mean Squared Error
* **WMAE** — Weighted Mean Absolute Error

### Evaluation Results

| Model       |        MAE |       RMSE |       WMAE |
| ----------- | ---------: | ---------: | ---------: |
| ARMA        |     1.659M |     2.269M |     1.549M |
| SARMA       |     2.129M |     2.504M |     1.797M |
| **Prophet** | **1.129M** | **1.579M** | **1.303M** |
| LSTM        |     1.889M |     2.074M |     1.921M |

Based on the validation results in this project, **Prophet produced the lowest WMAE** among the tested models and was therefore used for the final forecasting dashboard.

## Business Impact

The forecast is converted into practical planning signals for different business functions.

### Inventory Planning

Forecasts and upper prediction ranges can help identify high-demand weeks and support inventory preparation.

### Staffing

High-demand periods can be identified to support workforce planning.

### Supply Chain

Forecast information can help teams review replenishment requirements and capacity.

### Finance

Expected sales provide a forecasting signal for financial planning.

### Transportation

High-demand periods can be used to review delivery and transportation capacity.

## Interactive Dashboard

The project includes a React-based dashboard for generating and visualizing forecasts.

Users can:

* Select any calendar date
* Select the forecast horizon
* Generate future weekly predictions
* View expected sales
* View lower and upper forecast ranges
* Identify high-demand weeks
* View business planning recommendations
* Review detailed weekly predictions

### Date Handling

The user can select **any calendar date**.

Because the underlying Walmart dataset contains weekly observations represented on Fridays, the system converts a non-Friday selected date to the **next Friday** as the weekly forecast anchor.

For example:

```text
Selected Date
2028-11-18
     ↓
Weekly Forecast Anchor
2028-11-24
     ↓
Weekly Predictions
2028-11-24
2028-12-01
2028-12-08
...
```

This allows flexible calendar selection while keeping predictions aligned with the weekly structure of the dataset.

## Technology Stack

### Machine Learning / Data Science

* Python
* Pandas
* NumPy
* Scikit-learn
* Statsmodels
* Prophet
* TensorFlow / Keras

### Visualization

* Matplotlib
* Seaborn

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI

## Project Structure

```text
Walmart-Sales-Forecasting/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_eda_and_patterns.ipynb
│   ├── 03_seasonality_analysis.ipynb
│   ├── 04_anomaly_analysis.ipynb
│   ├── 05_feature_engineering.ipynb
│   ├── 06_arma_sarma_forecasting.ipynb
│   ├── 07_modern_forecasting.ipynb
│   ├── 08_lstm_forecasting.ipynb
│   └── 09_model_comparison_and_business.ipynb
│
├── outputs/
│   ├── figures/
│   ├── models/
│   └── reports/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── models/
│
├── frontend/
│   └── dashboard/
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Production Workflow

A possible production workflow for the system is:

```text
New Weekly Sales Data
        ↓
Data Validation
        ↓
Prophet Forecast
        ↓
Forecast Monitoring
        ↓
Demand / Error Alerts
        ↓
Business Action
        ↓
Periodic Model Retraining
```

A practical starting strategy for this project is **weekly forecasting and monitoring with periodic model retraining**. The current project demonstrates this workflow using the historical Walmart dataset rather than a live Walmart data stream.

## Future Enhancements

* Connect the system to a live sales data source
* Store forecasts in a database
* Add automated model retraining
* Add email/dashboard alerts
* Forecast at individual Store–Department level
* Add automated model monitoring
* Deploy the complete system to the cloud
* Add authentication and user management

## Conclusion

This project demonstrates an end-to-end approach to **retail sales forecasting**, from data exploration and anomaly analysis to model comparison, Prophet-based forecasting, business impact analysis, and interactive visualization.

> **Goal: Transform historical Walmart sales data into actionable weekly forecasts for better business planning.**
