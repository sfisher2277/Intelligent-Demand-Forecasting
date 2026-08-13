# Intelligent Demand Forecasting — Executive Summary

**Author:** Shawn Fisher
**Dataset:** Rossmann Store Sales (1,115 stores, ~2.5 years of daily sales)
**Full technical analysis:** see the `R/` notebooks (01–05) or their knitted HTML versions in `docs/`. **Production pipeline:** see `python/` for the full implementation (pipeline, API, Docker).

## The Business Question

Retailers need reliable sales forecasts to guide inventory, staffing, and promotion decisions. This project asks: **how much can a systematic, data-driven forecast improve on simple historical-pattern methods, and what does that improvement actually depend on?**

## What Was Done

The project moved through five stages, each building on the last:

1. **Business framing** — defined what "good" looks like for this problem and named the asymmetric cost of forecast errors (running out of stock is typically more costly than having too much).
2. **Exploratory analysis** — investigated seasonality, promotions, store differences, and several data anomalies to understand what actually drives sales.
3. **Baseline forecasts** — simple time series methods (seasonal naive,ETS, ARIMA) that use only historical sales patterns.
4. **Feature-based models** — a linear model (GLM) and a random forest,both given real business inputs (promotions, holidays, store type) that the baseline methods couldn't see.
5. **Evaluation** — compared all five models on accuracy, bias, and consistency across different store types and days of the week.

## Key Findings

**Giving a model access to real business information mattered far more than which algorithm was used.** The jump from the best simple time series method (16.9% average error) to a model that could see promotions and holidays (5.76% error) was roughly a 3x improvement. The jump from that model to a more sophisticated algorithm (5.43% error) was much smaller by comparison.

**The more sophisticated model's real advantage shows up in the hardest cases, not the average case.** For typical stores on typical days, the simple and sophisticated feature-based models perform almost identically. But for atypical situations — a small subset of stores open on Sundays, or an unusual store format that doesn't respond normally to promotions — the more sophisticated model was dramatically more accurate (up to 47 percentage points better in the hardest case).

**No single model is the unambiguous "best" choice** — it depends on the use case. A simpler model is easier to explain to non-technical stakeholders and loses very little accuracy for most stores. A more complex model is worth the added opacity specifically for the stores and situations that behave unusually.

## Recommendation

Use the interpretable model as the default for general reporting and executive-level forecasts, where explaining *why* a number changed matters. Reserve the more complex model for known atypical segments, where its accuracy advantage is largest and most valuable.

## From Analysis to Production

The recommended model above was then rebuilt as a complete, runnable prediction pipeline in Python — not just a research finding, but something that could actually be deployed and queried like a real business tool:

- **Automated pipeline** — data ingestion, feature engineering, and model training are fully scripted and repeatable, not manual notebook steps.
- **Experiment tracking** — every training run and its accuracy metrics are automatically logged, so model versions can be compared over time.
- **A live prediction service** — the model is served through a web API: given a store's characteristics for a given day, it returns a sales forecast on demand.
- **Containerized** — the entire service is packaged with Docker, so it can run identically on any machine without manual setup.
- **Tested** — the pipeline has automated tests that verify the data processing logic behaves correctly, catching potential errors before they reach a trained model.

This mirrors the path a forecasting model would actually take inside a company: from an analytical recommendation to a maintained, monitored system that other tools and teams can rely on.

## A Note on Tooling

This project was built with the assistance of Claude (Anthropic) for code drafting, debugging, and analytical framing throughout. All modeling decisions, hypothesis testing, and interpretation of results reflect my own analysis and understanding of both R and the underlying statistics.
