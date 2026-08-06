import dagshub
import mlflow
import pandas as pd
from sklearn.metrics import (
    mean_absolute_percentage_error,
    root_mean_squared_error,
    mean_absolute_error,
)

dagshub.init(repo_owner='sfisher2277', repo_name='Intelligent-Demand-Forecasting', mlflow=True)


def compute_metrics(y_true, y_pred) -> dict:
    """
    Compute standard regression metrics for forecast evaluation.

    Args:
        y_true: actual values
        y_pred: predicted values

    Returns:
        dictionary of metric name -> value
    """
    return {
        "mape": mean_absolute_percentage_error(y_true, y_pred),
        "rmse": root_mean_squared_error(y_true, y_pred),
        "mae": mean_absolute_error(y_true, y_pred),
    }


def get_run_history(experiment_name: str, max_results: int = 100) -> pd.DataFrame:
    """
    Pull all logged runs for an experiment from MLflow.

    Args:
        experiment_name: name of the MLflow experiment (e.g. "rossmann-forecasting")
        max_results: maximum number of runs to retrieve

    Returns:
        DataFrame of runs, one row per run, with params.* and metrics.* columns
    """
    return mlflow.search_runs(
        experiment_names=[experiment_name],
        max_results=max_results,
        order_by=["start_time DESC"],
    )


def compare_runs(
    experiment_name: str,
    metric: str = "metrics.rmse",
    top_n: int = 5,
) -> pd.DataFrame:
    """
    Rank runs from an experiment by a chosen metric.

    Args:
        experiment_name: name of the MLflow experiment
        metric: full metric column name to sort by (e.g. "metrics.rmse")
        top_n: number of top runs to keep

    Returns:
        DataFrame with run_id, start_time, params, and metrics,
        best-to-worst on `metric`
    """
    runs = get_run_history(experiment_name)

    if runs.empty:
        return runs

    lower_is_better = any(m in metric for m in ["rmse", "mape", "mae"])
    ranked = runs.sort_values(metric, ascending=lower_is_better).head(top_n)

    keep_cols = ["run_id", "start_time"] + [
        c for c in ranked.columns if c.startswith("params.") or c.startswith("metrics.")
    ]
    return ranked[keep_cols].reset_index(drop=True)


if __name__ == "__main__":
    experiment_name = "rossmann-forecasting"
    results = compare_runs(experiment_name, metric="metrics.rmse", top_n=5)

    if results.empty:
        print(f"No runs found for experiment '{experiment_name}'.")
    else:
        print(f"Top {len(results)} runs for '{experiment_name}' by RMSE:\n")
        print(results.to_string(index=False))