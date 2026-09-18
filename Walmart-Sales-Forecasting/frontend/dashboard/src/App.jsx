import React, { useState } from "react";

import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from "recharts";

import "./App.css";

/* ============================================================
   FORMAT FUNCTIONS
   ============================================================ */

function formatIndian(value) {
  if (value === undefined || value === null || isNaN(value)) {
    return "₹0";
  }

  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(value);
}

function formatCrore(value) {
  if (value === undefined || value === null || isNaN(value)) {
    return "₹0.00 Cr";
  }

  return `₹${(value / 10000000).toFixed(2)} Cr`;
}

/* ============================================================
   DATE HELPERS
   ============================================================ */

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function parseDate(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);

  return new Date(year, month - 1, day);
}

/*
   Convert any selected calendar date to the next Friday.

   JavaScript:
   Sunday    = 0
   Monday    = 1
   Tuesday   = 2
   Wednesday = 3
   Thursday  = 4
   Friday    = 5
   Saturday  = 6
*/

function getForecastFriday(dateString) {
  const date = parseDate(dateString);

  const day = date.getDay();

  // If already Friday
  if (day === 5) {
    return formatDate(date);
  }

  // Number of days until next Friday
  const daysUntilFriday = (5 - day + 7) % 7;

  date.setDate(date.getDate() + daysUntilFriday);

  return formatDate(date);
}

/* ============================================================
   CUSTOM CALENDAR
   ALL DAYS ENABLED
   NO FRIDAY HIGHLIGHTING
   ============================================================ */

function DateCalendar({ value, onChange }) {
  const selectedDate = parseDate(value);

  const [currentMonth, setCurrentMonth] = useState(
    new Date(
      selectedDate.getFullYear(),
      selectedDate.getMonth(),
      1
    )
  );

  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const daysInMonth = lastDay.getDate();
  const startingDay = firstDay.getDay();

  const days = [];

  /* Empty spaces before first day */

  for (let i = 0; i < startingDay; i++) {
    days.push(null);
  }

  /* All days */

  for (let day = 1; day <= daysInMonth; day++) {
    days.push(
      new Date(year, month, day)
    );
  }

  const monthName = currentMonth.toLocaleString(
    "en-US",
    {
      month: "long",
      year: "numeric",
    }
  );

  function previousMonth() {
    setCurrentMonth(
      new Date(year, month - 1, 1)
    );
  }

  function nextMonth() {
    setCurrentMonth(
      new Date(year, month + 1, 1)
    );
  }

  function selectDate(date) {
    if (!date) return;

    onChange(formatDate(date));
  }

  return (
    <div className="calendar-wrapper">

      {/* CALENDAR HEADER */}

      <div className="calendar-header">

        <button
          type="button"
          className="calendar-nav"
          onClick={previousMonth}
        >
          ◀
        </button>

        <div className="calendar-month">
          {monthName}
        </div>

        <button
          type="button"
          className="calendar-nav"
          onClick={nextMonth}
        >
          ▶
        </button>

      </div>

      {/* WEEK DAYS */}

      <div className="calendar-weekdays">

        <div>Sun</div>
        <div>Mon</div>
        <div>Tue</div>
        <div>Wed</div>
        <div>Thu</div>
        <div>Fri</div>
        <div>Sat</div>

      </div>

      {/* DAYS */}

      <div className="calendar-days">

        {days.map((date, index) => {

          if (!date) {
            return (
              <div
                key={index}
                className="calendar-empty"
              />
            );
          }

          const selected =
            formatDate(date) === value;

          return (
            <button
              key={formatDate(date)}
              type="button"
              className={`calendar-day ${
                selected ? "selected-day" : ""
              }`}
              onClick={() => selectDate(date)}
            >
              {date.getDate()}
            </button>
          );

        })}

      </div>

      <div className="calendar-info">
        📅 Select any calendar date
      </div>

    </div>
  );
}

/* ============================================================
   MAIN APP
   ============================================================ */

function App() {

  /* User-selected date.
     This can be ANY day. */

  const [startDate, setStartDate] =
    useState("2026-01-02");

  const [weeks, setWeeks] =
    useState(52);

  const [data, setData] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [showCalendar, setShowCalendar] =
    useState(false);

  /* ==========================================================
     GENERATE FORECAST
     ========================================================== */

  async function generateForecast() {

    setError("");
    setLoading(true);

    try {

      /*
        IMPORTANT:

        User can select ANY date.

        Example:

        Monday    → next Friday
        Wednesday → next Friday
        Friday    → same Friday
        Saturday  → next Friday
        Sunday    → next Friday

        This keeps the Prophet forecast weekly.
      */

      const forecastStartDate =
        getForecastFriday(startDate);

      console.log(
        "User selected date:",
        startDate
      );

      console.log(
        "Forecast Friday:",
        forecastStartDate
      );

      const response =
        await fetch(
          "https://walmart-sales-forecasting-kzgb.onrender.com/api/predict",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              /*
                Send the converted Friday
                to the backend.
              */
              start_date:
                forecastStartDate,

              weeks:
                Number(weeks),
            }),
          }
        );

      const result =
        await response.json();

      if (!response.ok) {

        throw new Error(
          result.detail ||
          result.error ||
          "Forecast request failed."
        );

      }

      if (result.error) {

        throw new Error(
          result.error
        );

      }

      setData(result);

    } catch (err) {

      setError(
        err.message ||
        "Unable to generate forecast."
      );

    } finally {

      setLoading(false);

    }

  }

  /* ==========================================================
     RESET
     ========================================================== */

  function resetForecast() {

    setData(null);

    setError("");

    setStartDate(
      "2026-01-02"
    );

    setWeeks(52);

    setShowCalendar(false);

  }

  /* ============================================================
     MAIN UI
     ============================================================ */

  return (

    <div className="app">

      <main className="dashboard">

        {/* ==================================================
            HEADER
           ================================================== */}

        <header className="header">

          <div>

            <h1>
              AI-Powered Walmart Sales
              Forecasting Dashboard
            </h1>

            <p>
              Prophet-based weekly sales
              forecasting and business planning
            </p>

          </div>

          <div className="model-badge">
            Prophet Model
          </div>

        </header>

        {/* ==================================================
            FORECAST CONTROL
           ================================================== */}

        <section className="forecast-control">

          <h2>
            Generate Future Sales Forecast
          </h2>

          <p className="control-description">
            Select any calendar date to generate
            weekly Walmart sales predictions.
          </p>

          <div className="control-grid">

            {/* =================================================
                DATE
               ================================================= */}

            <div className="control-group">

              <label>
                Forecast Start Date
              </label>

              {/* DATE BOX */}

              <div className="date-picker-container">

                <div className="date-input-box">

                  <div className="selected-date">

                    {startDate}

                  </div>

                  <button
                    type="button"
                    className="calendar-button"
                    onClick={() =>
                      setShowCalendar(
                        !showCalendar
                      )
                    }
                    title="Open calendar"
                  >
                    📅
                  </button>

                </div>

                {/* CALENDAR */}

                {showCalendar && (

                  <div className="calendar-dropdown">

                    <DateCalendar
                      value={startDate}
                      onChange={(date) => {

                        setStartDate(date);

                        setShowCalendar(false);

                      }}
                    />

                  </div>

                )}

              </div>

             

            </div>

            {/* =================================================
                WEEKS
               ================================================= */}

            <div className="control-group">

              <label>
                Forecast Horizon
              </label>

              <div className="week-options">

                {[4, 8, 12, 16, 24, 52].map(
                  (option) => (

                    <button
                      key={option}
                      type="button"
                      className={
                        weeks === option
                          ? "active"
                          : ""
                      }
                      onClick={() =>
                        setWeeks(option)
                      }
                    >
                      {option} weeks
                    </button>

                  )
                )}

              </div>

              <div className="control-actions">

                <button
                  type="button"
                  className="forecast-button"
                  onClick={generateForecast}
                  disabled={loading}
                >

                  {loading
                    ? "Generating..."
                    : "Generate Forecast"}

                </button>

                <button
                  type="button"
                  className="reset-button"
                  onClick={resetForecast}
                >
                  New Forecast
                </button>

              </div>

            </div>

          </div>

          {/* INFO */}

          

          {/* ERROR */}

          {error && (

            <div className="error-message">

              ⚠️ {error}

            </div>

          )}

        </section>

        {/* ==================================================
            RESULTS
           ================================================== */}

        {data && (

          <>

            {/* FORECAST PERIOD */}

          <div className="forecast-period">

  <div>
    <strong>Selected Date:</strong>{" "}
    {startDate}
  </div>

  <div>
    <strong>Weekly Forecast Anchor:</strong>{" "}
    {data.start_date}
  </div>

  <div>
    <strong>Forecast Period:</strong>{" "}
    {data.start_date}
    {" → "}
    {data.end_date}
    {" | "}
    {data.weeks} weeks
  </div>

</div>

            {/* SUMMARY */}

            <section className="summary-grid">

              <div className="summary-card">

                <h3>
                  Average Weekly Sales
                </h3>

                <div className="summary-value">

                  {formatCrore(
                    data.summary.average_sales
                  )}

                </div>

              </div>

              <div className="summary-card">

                <h3>
                  Maximum Weekly Sales
                </h3>

                <div className="summary-value">

                  {formatCrore(
                    data.summary.maximum_sales
                  )}

                </div>

              </div>

              <div className="summary-card">

                <h3>
                  Minimum Weekly Sales
                </h3>

                <div className="summary-value">

                  {formatCrore(
                    data.summary.minimum_sales
                  )}

                </div>

              </div>

              <div className="summary-card">

                <h3>
                  High Demand Weeks
                </h3>

                <div className="summary-value">

                  {data.summary.high_demand_weeks}

                </div>

              </div>

            </section>

            {/* =================================================
                SALES FORECAST
               ================================================= */}

            <section className="card chart-card">

              <div className="section-title">

                <div>

                  <h2>
                    Sales Forecast
                  </h2>

                  <p>
                    Expected sales with forecast
                    uncertainty range
                  </p>

                </div>

              </div>

              <div className="chart-container">

                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >

                  <ComposedChart
                    data={data.predictions}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 55,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="date"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval="preserveStartEnd"
                    />

                    <YAxis
                      tickFormatter={(value) =>
                        `₹${(
                          value / 10000000
                        ).toFixed(1)}Cr`
                      }
                    />

                    <Tooltip
                      formatter={(value) =>
                        `₹${formatIndian(value)}`
                      }
                    />

                    <Area
                      type="monotone"
                      dataKey="forecast_upper"
                      stroke="none"
                      fill="#bfdbfe"
                      fillOpacity={0.45}
                      name="Upper Forecast"
                    />

                    <Area
                      type="monotone"
                      dataKey="forecast_lower"
                      stroke="none"
                      fill="#ffffff"
                      fillOpacity={1}
                      name="Lower Forecast"
                    />

                    <Line
                      type="monotone"
                      dataKey="predicted_sales"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={false}
                      name="Expected Sales"
                    />

                  </ComposedChart>

                </ResponsiveContainer>

              </div>

            </section>

            {/* =================================================
                BUSINESS IMPACT
               ================================================= */}

            <section className="card">

              <div className="section-title">

                <div>

                  <h2>
                    Business Impact
                  </h2>

                  <p>
                    How forecast information can
                    support business planning
                  </p>

                </div>

              </div>

              <div className="business-grid">

                <div className="business-card">

                  <div className="business-icon">
                    📦
                  </div>

                  <h3>
                    PLAN INVENTORY
                  </h3>

                  <p>
                    {
                      data.business_impact.inventory.action
                    }
                  </p>

                  <strong>
                    Planning Value:{" "}
                    {formatCrore(
                      data.business_impact
                        .inventory
                        .planning_value
                    )}
                  </strong>

                </div>

                <div className="business-card">

                  <div className="business-icon">
                    👥
                  </div>

                  <h3>
                    PREPARE STAFFING
                  </h3>

                  <p>
                    {
                      data.business_impact.staffing.action
                    }
                  </p>

                </div>

                <div className="business-card">

                  <div className="business-icon">
                    🚚
                  </div>

                  <h3>
                    PREPARE SUPPLY
                  </h3>

                  <p>
                    {
                      data.business_impact
                        .supply_chain
                        .action
                    }
                  </p>

                </div>

                <div className="business-card">

                  <div className="business-icon">
                    💰
                  </div>

                  <h3>
                    SALES PLANNING SIGNAL
                  </h3>

                  <p>
                    Expected sales for the
                    selected forecast period.
                  </p>

                  <strong>
                    Expected Sales:{" "}
                    {formatCrore(
                      data.business_impact
                        .finance
                        .expected_sales
                    )}
                  </strong>

                </div>

                <div className="business-card">

                  <div className="business-icon">
                    🚛
                  </div>

                  <h3>
                    REVIEW DELIVERY CAPACITY
                  </h3>

                  <p>
                    {
                      data.business_impact
                        .transportation
                        .action
                    }
                  </p>

                </div>

              </div>

            </section>

            {/* =================================================
                UNCERTAINTY
               ================================================= */}

            <section className="card">

              <div className="section-title">

                <div>

                  <h2>
                    Forecast Uncertainty
                  </h2>

                  <p>
                    Prediction interval for the
                    selected forecast period
                  </p>

                </div>

              </div>

              <div className="uncertainty-grid">

                <div className="uncertainty-card">

                  <span>
                    Total Lower Forecast
                  </span>

                  <strong>
                    {formatCrore(
                      data.summary
                        .forecast_minimum
                    )}
                  </strong>

                </div>

                <div className="uncertainty-card">

                  <span>
                    Total Expected Sales
                  </span>

                  <strong>
                    {formatCrore(
                      data.summary
                        .total_expected_sales
                    )}
                  </strong>

                </div>

                <div className="uncertainty-card">

                  <span>
                    Total Upper Forecast
                  </span>

                  <strong>
                    {formatCrore(
                      data.summary
                        .forecast_maximum
                    )}
                  </strong>

                </div>

                <div className="uncertainty-card">

                  <span>
                    Total Planning Value
                  </span>

                  <strong>
                    {formatCrore(
                      data.summary
                        .total_planning_value
                    )}
                  </strong>

                </div>

              </div>

            </section>

            {/* =================================================
                TABLE
               ================================================= */}

            <section className="card">

              <div className="section-title">

                <div>

                  <h2>
                    Weekly Forecast Details
                  </h2>

                  <p>
                    Detailed prediction for each
                    forecast week
                  </p>

                </div>

              </div>

              <div className="table-container">

                <table>

                  <thead>

                    <tr>

                      <th>Date</th>

                      <th>
                        Expected Sales
                      </th>

                      <th>
                        Lower Forecast
                      </th>

                      <th>
                        Upper Forecast
                      </th>

                      <th>
                        Planning Buffer
                      </th>

                      <th>
                        Recommended Inventory
                      </th>

                      <th>
                        Demand Status
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {data.predictions.map(
                      (item) => (

                        <tr
                          key={item.date}
                        >

                          <td>
                            {item.date}
                          </td>

                          <td>
                            ₹
                            {formatIndian(
                              item.predicted_sales
                            )}
                          </td>

                          <td>
                            ₹
                            {formatIndian(
                              item.forecast_lower
                            )}
                          </td>

                          <td>
                            ₹
                            {formatIndian(
                              item.forecast_upper
                            )}
                          </td>

                          <td>
                            ₹
                            {formatIndian(
                              item.planning_buffer
                            )}
                          </td>

                          <td>
                            ₹
                            {formatIndian(
                              item.recommended_inventory
                            )}
                          </td>

                          <td>

                            <span
                              className={`demand-status ${
                                item.demand_status ===
                                "HIGH DEMAND"
                                  ? "high"
                                  : "normal"
                              }`}
                            >

                              {
                                item.demand_status
                              }

                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            </section>

            {/* =================================================
                MODEL NOTE
               ================================================= */}

            

          </>

        )}

        {/* ==================================================
            WELCOME
           ================================================== */}

        {!data && !loading && (

          <section className="welcome-card">

            <div className="welcome-icon">
              📊
            </div>

            <h2>
              Ready to Generate a Forecast?
            </h2>

            <p>

              Select <strong>any date</strong>,
              choose your forecast horizon,
              and click{" "}
              <strong>
                Generate Forecast
              </strong>{" "}
              to view weekly sales predictions
              and business planning insights.

            </p>

          </section>

        )}

        {/* ==================================================
            FOOTER
           ================================================== */}

        

      </main>

    </div>

  );
}

export default App;
