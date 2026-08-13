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


### July 27, 2026

**Did:**
- Built 04_feature_model.Rmd: store-day level feature model using
  Promo, DayOfWeek, StateHoliday, SchoolHoliday, StoreType,
  Assortment, CompetitionDistance (+ missingness flag)
- Fit and evaluated a GLM, then a random forest (ranger via
  tidymodels), both at store-day level and rolled up to daily
  aggregate for apples-to-apples comparison with Phase 4 baselines
- Deliberately excluded Customers as a feature (not known in advance
  in a real forecasting scenario — would be data leakage)
- Sped up random forest fit using ranger's built-in num.threads
  parallelism (not doParallel/foreach, which doesn't apply to a
  single fit() call)

**Found:**
- GLM's Promo coefficient (~35% implied lift) closely matched EDA's
  ~39% aggregate figure — good sanity check
- GLM confirmed Monday/Sunday as highest-sales weekdays, consistent
  with EDA
- Full aggregate comparison table:
  - SNAIVE: 17.4% MAPE / 1.78M RMSE
  - ETS: 16.9% MAPE / 1.42M RMSE
  - ARIMA: 21.8% MAPE / 1.34M RMSE
  - GLM: 5.76% MAPE / 616K RMSE
  - Random Forest: 5.43% MAPE / 541K RMSE
- The big accuracy jump was baseline -> GLM (access to Promo/holiday
  info), not GLM -> random forest (model complexity) — feature
  access mattered more than algorithm sophistication here
- Feature model resolved the severe Monday over-forecasting bias
  found in Phase 4 baselines (SNAIVE: -2.42M -> GLM: +117 MeanError)
- New, smaller issue surfaced: Sunday now has the highest error,
  explained by only 33 of 1,115 stores ever being open on Sunday —
  small, atypical subgroup, likely underrepresented in training
- Random forest's top feature was CompetitionDistance, not Promo —
  investigated with a smoothed plot and found a nonlinear,
  counterintuitive relationship (closer competition = higher sales),
  most likely because CompetitionDistance is a proxy for store
  location density (urban/high-traffic vs. rural), not a direct
  causal effect of competition itself
- Random forest slightly more biased than GLM (+106K vs +70K ME)
  despite being more accurate overall — noted rather than glossed
  over

**Questions / next steps:**
- Phase 5 (feature-driven forecasting) is complete
- Next: Phase 6 — formal model comparison write-up, tying accuracy
  gains back to the "cost of being wrong" business framing from
  Phase 2
- Possible follow-up (lower priority): investigate whether Sunday's
  small-sample issue is worth a separate handling approach, or just
  a documented limitation
  rather than pure aggregate, given known store-to-store variation
  from EDA
- Possible follow-up (lower priority): investigate whether the
  specific week SNAIVE copied from for Monday was itself anomalous


### July 29, 2026

**Did:**
- Built 05_model_evaluation.Rmd: consolidated comparison of all five
  models (SNAIVE, ETS, ARIMA, GLM, Random Forest) on the same
  aggregate scale
- Added conditional accuracy breakdowns by weekday, Promo, and
  StoreType for GLM vs. Random Forest
- Translated MAPE into an illustrative daily-dollar-error figure to
  connect back to the cost-of-being-wrong framing from Phase 2
- Wrote a final recommendation section weighing interpretability
  (GLM) against targeted accuracy gains (Random Forest)
- Added an AI tooling disclosure to the README

**Found:**
- Full model ranking by aggregate MAPE: RF (5.43%) < GLM (5.76%) 
  ARIMA (21.8%) < ETS (16.9%)... wait, correct order: RF < GLM 
  ETS < SNAIVE < ARIMA
- Random Forest's advantage over GLM is NOT uniform — it's small
  and consistent for Promo (~6-7 pts) but dramatically larger for
  atypical, underrepresented segments: Sunday (-47 pts MAPE) and
  StoreType b (-23 pts MAPE)
- This means model choice should depend on use case: GLM's
  interpretability may outweigh its small accuracy gap for
  high-level/executive reporting, while Random Forest earns its
  complexity specifically for atypical stores/days
- Random Forest carries a slightly higher bias toward
  overforecasting than GLM (+106K vs +70K ME) — a real tradeoff
  worth naming given underforecasting/stockouts were framed as the
  costlier error type in the business understanding doc
- Final recommendation: no single winner — GLM for
  interpretability/executive use, Random Forest specifically flagged
  for known atypical segments

**Questions / next steps:**
- Phase 6 complete — core analytical arc of the project (business
  understanding through evaluation/recommendation) is done
- Next: housekeeping (README roadmap update, confirm all notebooks
  knit cleanly from a fresh session) + draft a plain-language
  executive summary as a standalone, non-technical artifact
- Phase 7 (Python translation) deferred until Python for Data
  Analysis coursework begins next semester


### July 29, 2026 (cont.)

**Did:**
- Discussed next steps after completing Phase 6
- Decided against starting a new portfolio project or the Rossmann
  API idea for now
- Decided to pursue Phase 7 (Python translation) when ready, scoped
  down from the original plan: start with just 02_data_exploration
  translated to pandas/matplotlib, not the full project, and not the
  modeling notebooks until sklearn is covered in coursework

**Questions / next steps:**
- When ready: set up python/ subfolder, keep R version intact
  alongside it, translate EDA notebook chunk by chunk (write fresh,
  don't transliterate line-by-line — that's where the actual
  learning happens)


### August 4, 2026

**Did:**
- Started Phase 7: Python translation, beginning with 02_data_exploration
- Set up demand-forecasting conda environment (pandas, numpy, matplotlib,
  jupyter) via conda-forge channel
- Reorganized repo: analysis/ -> R/, added python/, moved knitted HTML
  to docs/, updated README and LinkedIn Featured links accordingly
- Translated: data load with explicit dtype handling, structure/
  missingness check, merge, aggregate daily sales plot, sample store
  plots

**Found:**
- Pandas requires explicit dtype specification at read time
  (dtype={"StateHoliday": str}) to avoid mixed-type warnings — R's
  readr handles this more gracefully by default
- groupby() in pandas returns Date as an index, not a column —
  needs .reset_index(), no dplyr equivalent for this gotcha
- Investigated an apparent extended closure in a sample store plot
  (looked like the same renovation-closure pattern found in R);
  turned out to be a normal, regularly Sunday-closed store — the
  "closure" was a rendering artifact from viewing a compressed
  multi-year timescale, not a real anomaly. Confirmed with a zoomed,
  marker-point plot.
- SQL fluency (used daily at work) maps more directly onto pandas
  than R does in several places — groupby/agg ~ GROUP BY, merge ~
  JOIN, boolean masking ~ WHERE/BETWEEN — useful mental shortcut
  going forward

**Questions / next steps:**
- Continue 02_data_exploration.ipynb: promo effect, StateHoliday and
  Assortment breakdowns, anomaly check (open + zero sales) — mirror
  the same checks already done in R
- Remember: & / | (not and/or) with explicit parentheses for
  compound pandas filters


  ### August 7, 2026

**Did:**
- Built evaluate.py: compute_metrics() (standalone MAPE/RMSE/MAE calc,
  pulled out of train_model()), get_run_history() and compare_runs()
  (query and rank MLflow runs via the tracking API)
- Wired train.py to call compute_metrics() instead of duplicating the
  metric calculation inline; train_model() now logs mae alongside
  mape/rmse for the first time
- Fixed a missing entrypoint in train.py — the ingest -> build_features
  -> train_model chain was only ever run manually from the pipeline
  demo notebook; added an if __name__ == "__main__" block so
  `python train.py` runs the full pipeline standalone
- Built the FastAPI /predict endpoint (api/main.py): Pydantic request
  schema, manual one-hot encoding for StoreType/Assortment (single-row
  requests can't use pd.get_dummies the way build_features does),
  reindexes by model.feature_names_in_ before predicting
- Tested /predict end-to-end via the FastAPI /docs UI — confirmed
  working, sensible non-zero prediction for realistic input
- General tooling cleanup: fixed .gitignore (was missing the intended
  python/models/* exclusion; added .ipynb_checkpoints/ too and
  untracked already-committed checkpoint files), moved primary working
  environment from Jupyter/standalone terminal to VS Code as a single
  folder window

**Found:**
- mlflow.sklearn.log_model() on a recent MLflow version registers a
  "Logged Model" entity (its own Model ID) rather than just a plain
  run artifact — client.list_artifacts() on the run came back empty
  even though DagsHub's UI showed the model. Loading via
  models:/{model_id} hung indefinitely rather than erroring, which
  looked like a DagsHub/MLflow version compatibility gap on that
  specific endpoint rather than anything wrong with the run itself
- Decided to sidestep rather than debug further: train.py now also
  saves the model locally via joblib (python/models/model.pkl,
  gitignored), and the API loads from disk instead of hitting MLflow
  at request time — decouples experiment tracking (still fully
  MLflow-based) from serving, which is a normal pattern and arguably
  cleaner architecture anyway
- PowerShell's default execution policy blocked conda's own
  activation hook script from running in new terminals, silently
  breaking `conda activate` — fixed once with
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

**Questions / next steps:**
- Dockerize the API (last item on the original pipeline roadmap)
- Minor: mlflow.sklearn.log_model(model, "model") throws a deprecation
  warning (artifact_path -> name) — cosmetic, not urgent
- Decide whether python/models/model.pkl should be committed for
  reviewer convenience or left as "regenerate via train.py" — currently
  gitignored, consistent with how data/ is handled


  ### August 11, 2026

**Did:**
- Wrote real unit test coverage for the Python pipeline: test_ingest.py
  (schema validation failure modes, the store-metadata left-join edge
  case, an end-to-end ingest_data test using synthetic CSVs via
  pytest's tmp_path) and test_features.py (lag feature correctness,
  including a dedicated test confirming Sales_lag_1/7 don't leak
  across different stores via groupby, one-hot encoding, holiday
  flags, and the full build_features pipeline)
- 18/18 tests passing against the real ingest.py/features.py
- Fixed a couple of README issues: missing code fences that had
  collapsed the "Running the Prediction API" commands into a single
  unreadable paragraph, restructured that section since the old
  "Option A/B" framing incorrectly implied Docker was a fully
  standalone path (model.pkl is gitignored, so training via Python
  is a required first step regardless of how you serve it), and
  corrected a leftover "M.S." reference to M.D.A.

**Found:**
- All tests run against small synthetic DataFrames rather than the
  real Rossmann CSVs — fast (well under a second for all 18) and no
  dependency on the multi-million-row dataset being present locally

**Questions / next steps:**
- No open items on the original pipeline roadmap; project is
  feature-complete, documented, and tested
- Possible future add-ons (not urgent): cloud deployment of the API
  (Render/Railway/Fly.io) for a live demo URL beyond local Docker