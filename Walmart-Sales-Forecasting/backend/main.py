from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import joblib
import pandas as pd
import numpy as np
import os


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Walmart Sales Forecasting API",
    description="Prophet-based Walmart weekly sales forecasting API",
    version="2.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://sprightly-griffin-b90941.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "complete_business.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

MODEL_ERROR = None

try:

    model_data = joblib.load(MODEL_PATH)

    prophet_model = model_data["model"]

    business_data = model_data.get(
        "business_data",
        None
    )

    high_demand_threshold = float(
        model_data["high_demand_threshold"]
    )

    error_threshold = float(
        model_data["error_threshold"]
    )

    MODEL_LOADED = True

    print("=" * 60)
    print("MODEL LOADED SUCCESSFULLY")
    print(f"MODEL_PATH: {MODEL_PATH}")
    print("=" * 60)

except Exception as e:

    import traceback

    print("=" * 60)
    print("MODEL LOAD FAILED")
    print(f"MODEL_PATH: {MODEL_PATH}")
    print(f"File exists: {os.path.exists(MODEL_PATH)}")
    print(f"Error: {e}")
    traceback.print_exc()
    print("=" * 60)

    prophet_model = None
    business_data = None

    high_demand_threshold = 0
    error_threshold = 0

    MODEL_LOADED = False
    MODEL_ERROR = str(e)


# ============================================================
# REQUEST MODEL
# ============================================================

class PredictionRequest(BaseModel):

    start_date: str

    weeks: int = 12


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Walmart Sales Forecasting API is running",

        "model":
            "Prophet",

        "forecast_type":
            "Future weekly forecasting",

        "model_loaded":
            MODEL_LOADED

    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {

        "status":
            "healthy" if MODEL_LOADED else "model_error",

        "model":
            "Prophet",

        "model_loaded":
            MODEL_LOADED,

        "model_error":
            MODEL_ERROR

    }


# ============================================================
# BUSINESS IMPACT INFORMATION
# ============================================================

@app.get("/api/business-impact")
def business_impact():

    return {

        "high_demand_threshold":
            high_demand_threshold,

        "error_threshold":
            error_threshold,

        "business_areas": [

            "Inventory",
            "Staffing",
            "Supply Chain",
            "Finance",
            "Transportation"

        ]

    }


# ============================================================
# FORECAST API
# ============================================================

@app.post("/api/predict")
def predict(request: PredictionRequest):

    try:

        # ====================================================
        # 1. CHECK MODEL
        # ====================================================

        if not MODEL_LOADED:

            return {

                "error":
                    "Prophet model could not be loaded.",

                "details":
                    MODEL_ERROR

            }


        # ====================================================
        # 2. VALIDATE NUMBER OF WEEKS
        # ====================================================

        if request.weeks < 1:

            return {

                "error":
                    "Forecast weeks must be at least 1."

            }


        if request.weeks > 520:

            return {

                "error":
                    "Forecast weeks cannot exceed 520 weeks."

            }


        # ====================================================
        # 3. CONVERT START DATE
        # ====================================================

        start_date = pd.to_datetime(
            request.start_date
        )


        # ====================================================
        # 4. HISTORICAL TRAINING END
        # ====================================================

        training_end_date = pd.Timestamp(
            "2012-10-26"
        )


        if start_date <= training_end_date:

            return {

                "error":
                    "Start date must be after "
                    "the historical training period "
                    "(2012-10-26)."

            }


        # ====================================================
        # 5. REQUIRE FRIDAY
        # ====================================================

        if start_date.weekday() != 4:

            return {

                "error":
                    "Start date must be a Friday because "
                    "the Walmart dataset contains weekly "
                    "Friday observations."

            }


        # ====================================================
        # 6. CREATE FUTURE WEEKLY DATES
        # ====================================================

        future_dates = pd.date_range(

            start=start_date,

            periods=request.weeks,

            freq="W-FRI"

        )


        # ====================================================
        # 7. CREATE PROPHET INPUT
        # ====================================================

        future = pd.DataFrame({

            "ds":
                future_dates

        })


        # ====================================================
        # 8. GENERATE PROPHET FORECAST
        # ====================================================

        forecast = prophet_model.predict(
            future
        )


        # ====================================================
        # 9. CREATE PREDICTION RESULTS
        # ====================================================

        predictions = []


        for _, row in forecast.iterrows():

            predicted_sales = float(
                row["yhat"]
            )

            forecast_lower = float(
                row["yhat_lower"]
            )

            forecast_upper = float(
                row["yhat_upper"]
            )

            predicted_sales = max(
                0,
                predicted_sales
            )

            forecast_lower = max(
                0,
                forecast_lower
            )

            forecast_upper = max(
                0,
                forecast_upper
            )

            planning_buffer = (

                forecast_upper
                - predicted_sales

            )

            planning_buffer = max(
                0,
                planning_buffer
            )

            if predicted_sales >= high_demand_threshold:

                demand_status = "HIGH DEMAND"

            else:

                demand_status = "NORMAL"

            recommended_inventory = (

                predicted_sales
                + planning_buffer

            )

            predictions.append({

                "date":
                    row["ds"].strftime(
                        "%Y-%m-%d"
                    ),

                "predicted_sales":
                    round(
                        predicted_sales,
                        2
                    ),

                "forecast_lower":
                    round(
                        forecast_lower,
                        2
                    ),

                "forecast_upper":
                    round(
                        forecast_upper,
                        2
                    ),

                "planning_buffer":
                    round(
                        planning_buffer,
                        2
                    ),

                "recommended_inventory":
                    round(
                        recommended_inventory,
                        2
                    ),

                "demand_status":
                    demand_status

            })


        # ====================================================
        # 10. EXTRACT FORECAST VALUES
        # ====================================================

        predicted_values = [

            item["predicted_sales"]

            for item in predictions

        ]

        lower_values = [

            item["forecast_lower"]

            for item in predictions

        ]

        upper_values = [

            item["forecast_upper"]

            for item in predictions

        ]


        # ====================================================
        # 11. HIGH DEMAND COUNT
        # ====================================================

        high_demand_weeks = sum(

            1

            for item in predictions

            if item["demand_status"]
            == "HIGH DEMAND"

        )


        # ====================================================
        # 12. TOTAL FORECAST VALUES
        # ====================================================

        total_expected_sales = sum(
            predicted_values
        )

        total_lower_forecast = sum(
            lower_values
        )

        total_upper_forecast = sum(
            upper_values
        )


        # ====================================================
        # 13. SUMMARY STATISTICS
        # ====================================================

        average_sales = float(
            np.mean(
                predicted_values
            )
        )

        maximum_sales = float(
            np.max(
                predicted_values
            )
        )

        minimum_sales = float(
            np.min(
                predicted_values
            )
        )


        # ====================================================
        # 14. END DATE
        # ====================================================

        end_date = future_dates[-1]


        # ====================================================
        # 15. RETURN COMPLETE RESPONSE
        # ====================================================

        return {

            "model":
                "Prophet",

            "forecast_type":
                "Future weekly forecast",

            "weeks":
                request.weeks,

            "start_date":
                start_date.strftime(
                    "%Y-%m-%d"
                ),

            "end_date":
                end_date.strftime(
                    "%Y-%m-%d"
                ),

            "predictions":
                predictions,

            "summary": {

                "average_sales":
                    round(
                        average_sales,
                        2
                    ),

                "maximum_sales":
                    round(
                        maximum_sales,
                        2
                    ),

                "minimum_sales":
                    round(
                        minimum_sales,
                        2
                    ),

                "high_demand_weeks":
                    high_demand_weeks,

                "forecast_minimum":
                    round(
                        total_lower_forecast,
                        2
                    ),

                "total_expected_sales":
                    round(
                        total_expected_sales,
                        2
                    ),

                "forecast_maximum":
                    round(
                        total_upper_forecast,
                        2
                    ),

                "total_planning_value":
                    round(
                        total_upper_forecast,
                        2
                    )

            },

            "business_impact": {

                "inventory": {

                    "title":
                        "PLAN INVENTORY",

                    "action":
                        f"Plan inventory for "
                        f"{high_demand_weeks} "
                        f"high-demand week(s) "
                        f"using the upper forecast range.",

                    "planning_value":
                        round(
                            total_upper_forecast,
                            2
                        )

                },

                "staffing": {

                    "title":
                        "PREPARE STAFFING",

                    "action":
                        f"Prepare additional staffing "
                        f"coverage for "
                        f"{high_demand_weeks} "
                        f"high-demand week(s).",

                    "high_demand_weeks":
                        high_demand_weeks

                },

                "supply_chain": {

                    "title":
                        "PREPARE SUPPLY",

                    "action":
                        f"Review replenishment capacity "
                        f"for "
                        f"{high_demand_weeks} "
                        f"high-demand week(s).",

                    "high_demand_weeks":
                        high_demand_weeks

                },

                "finance": {

                    "title":
                        "SALES PLANNING SIGNAL",

                    "expected_sales":
                        round(
                            total_expected_sales,
                            2
                        )

                },

                "transportation": {

                    "title":
                        "REVIEW DELIVERY CAPACITY",

                    "action":
                        f"Review delivery capacity "
                        f"for "
                        f"{high_demand_weeks} "
                        f"high-demand week(s).",

                    "high_demand_weeks":
                        high_demand_weeks

                }

            }

        }


    except Exception as e:

        import traceback
        traceback.print_exc()

        return {

            "error":
                "Prediction failed.",

            "details":
                str(e)

        }