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

except Exception as e:

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
            MODEL_LOADED

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


        # Maximum 10 years of weekly forecasts
        # 52 weeks × 10 years = 520 weeks

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
        #
        # Walmart historical dataset ends:
        #
        # 2012-10-26
        #
        # Future forecasting must start after
        # the historical period.
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
        #
        # Walmart data is weekly and the observations
        # are recorded on Fridays.
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

            # ------------------------------------------------
            # EXPECTED SALES
            # ------------------------------------------------

            predicted_sales = float(
                row["yhat"]
            )


            # ------------------------------------------------
            # LOWER FORECAST
            # ------------------------------------------------

            forecast_lower = float(
                row["yhat_lower"]
            )


            # ------------------------------------------------
            # UPPER FORECAST
            # ------------------------------------------------

            forecast_upper = float(
                row["yhat_upper"]
            )


            # ------------------------------------------------
            # PREVENT NEGATIVE SALES
            # ------------------------------------------------

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


            # ------------------------------------------------
            # PLANNING BUFFER
            # ------------------------------------------------
            #
            # Difference between upper forecast and
            # expected forecast.
            # ------------------------------------------------

            planning_buffer = (

                forecast_upper
                - predicted_sales

            )


            planning_buffer = max(
                0,
                planning_buffer
            )


            # ------------------------------------------------
            # HIGH DEMAND CLASSIFICATION
            # ------------------------------------------------

            if predicted_sales >= high_demand_threshold:

                demand_status = "HIGH DEMAND"

            else:

                demand_status = "NORMAL"


            # ------------------------------------------------
            # RECOMMENDED INVENTORY
            # ------------------------------------------------
            #
            # This is a planning signal.
            # It is NOT an actual Walmart inventory order.
            # ------------------------------------------------

            recommended_inventory = (

                predicted_sales
                + planning_buffer

            )


            # ------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------

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

            # ------------------------------------------------
            # FORECAST INFORMATION
            # ------------------------------------------------

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


            # ------------------------------------------------
            # WEEKLY PREDICTIONS
            # ------------------------------------------------

            "predictions":
                predictions,


            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

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


            # ------------------------------------------------
            # BUSINESS IMPACT
            # ------------------------------------------------

            "business_impact": {


                # ============================================
                # INVENTORY
                # ============================================

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


                # ============================================
                # STAFFING
                # ============================================

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


                # ============================================
                # SUPPLY CHAIN
                # ============================================

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


                # ============================================
                # FINANCE
                # ============================================

                "finance": {

                    "title":
                        "SALES PLANNING SIGNAL",

                    "expected_sales":
                        round(
                            total_expected_sales,
                            2
                        )

                },


                # ============================================
                # TRANSPORTATION
                # ============================================

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


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        return {

            "error":
                str(e)

        }
