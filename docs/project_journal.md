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
