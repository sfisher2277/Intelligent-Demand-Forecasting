### July 16, 2026

**Did:**
- Set up repo, RStudio ↔ Git workflow
- Wrote and pushed business understanding doc

**Found:**
- WFM background maps well onto retail forecasting audiences (staffing/service-level tradeoffs ≈ inventory/stockout tradeoffs)

**Questions / next steps:**
- Start EDA — how much do stores vary from each other? Does a single global model make sense?

### July 16, 2026

**Did:**
- Completed EDA on train.csv + store.csv (merged on Store)
- Checked structure/missingness, overall + individual store trends,
  promo effect, closures/zero-sales anomaly, StateHoliday and
  Assortment breakdowns

**Found:**
- Clear weekly seasonality + Christmas spike in aggregate sales
- Missingness concentrated in store.csv: CompetitionDistance,
  CompetitionOpenSinceMonth/Year, Promo2Since*/PromoInterval
  (roughly half of stores never ran Promo2)
- Some stores closed for extended periods in 2014 (sharp drop to
  zero, resumes normally on reopening) — likely refurbishment
- 54 store-days had Open=1 but Sales=0, not explained by
  StateHoliday/SchoolHoliday — flagged as data noise, not a real
  pattern, and left unresolved
- Promos increase sales ~39% on average, but this varies a lot by
  segment: StoreType a/c/d see 33–44% lift, StoreType b only ~18%
- Stores open on holidays (esp. Christmas, Easter) show higher
  avg sales than typical days — likely self-selection (stores that
  expect a rush choose to stay open), not a holiday effect broadly
- Assortment b showed a similarly weak promo response (~7.5%) —
  investigated overlap with StoreType b and found Assortment b is
  almost entirely nested within StoreType b (9 of 9 stores). Same
  small segment (17 stores total), not two independent findings.
- StoreType b / Assortment b results should be treated as
  low-confidence given the small n (17 stores)

**Questions / next steps:**
- Individual stores vary meaningfully — worth testing store-level
  vs. global models rather than assuming one approach fits all
- Decide how to handle the 54 anomalous zero-sales rows before
  modeling (drop vs. keep vs. flag as a feature)
- Decide how to handle missing CompetitionDistance/Promo2 fields
  (impute vs. flag vs. exclude as predictors)
- Next: pick a baseline forecasting approach


### July 20, 2026

**Did:**
- Set up time-based train/test split (last 6 weeks held out as test,
  matching Rossmann's real forecast horizon)
- Built and compared three baseline models on aggregate daily sales:
  SNAIVE (weekly lag), ETS, ARIMA
- Fixed deprecated autoplot() warning by installing/loading ggtime
- Evaluated all three on MAPE, RMSE, and ME (bias)

**Found:**
- ETS wins on MAPE (16.9%), ARIMA wins on RMSE, ARIMA has the least
  bias — no single model wins on every metric, consistent with
  expecting multiple metrics from the business understanding doc
- Corrected an earlier misread of ME's sign: negative ME means the
  models are OVER-forecasting, not under-forecasting
- All three models over-forecast most strongly on Mondays (SNAIVE
  worst by far, -2.42M) despite Monday being historically one of the
  highest-sales weekdays alongside Sunday
- Tested two hypotheses for the Monday effect and ruled both out:
  - Monday promo rate is NOT elevated vs. other weekdays (0.56,
    in line with Tue-Fri)
  - Per-store Monday average sales are nearly identical between
    train (8,216) and test (8,216) periods — no trend shift
- Most likely explanation: SNAIVE has no smoothing and copies the
  prior week's raw value forward, so noise from a single volatile
  week propagates directly into the forecast — a structural
  limitation, not a real behavioral pattern
- Confirmed store count dips ~1,100 to ~900 for roughly mid-2014
  to early 2015 (within training window, not test window) — not
  the driver of test-period bias, but may be quietly affecting
  ETS/ARIMA's learned seasonal parameters

**Questions / next steps:**
- Phase 4 (baseline models) is complete — ETS/ARIMA/SNAIVE all
  established as a floor to beat
- Start Phase 5: bring in Promo, StoreType, DayOfWeek, StateHoliday
  as actual model features rather than relying on pure time series
  structure
- Consider whether a feature model needs to run at store level
  rather than pure aggregate, given known store-to-store variation
  from EDA
- Possible follow-up (lower priority): investigate whether the
  specific week SNAIVE copied from for Monday was itself anomalous
