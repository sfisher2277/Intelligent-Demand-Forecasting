import yaml
import pandas as pd
import dagshub
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from evaluate import compute_metrics

dagshub.init(repo_owner='sfisher2277', repo_name='Intelligent-Demand-Forecasting', mlflow=True)
mlflow.set_experiment("rossmann-forecasting")

def load_config(config_path: str) -> dict:
    """
    Load model training configuration from YAML.
    
    Args:
        config_path: path to model_config.yaml
    
    Returns:
        dictionary of config values
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def train_model(df: pd.DataFrame, config: dict):
    """
    Train a Random Forest model on Rossmann sales data and log to MLflow.
    
    Args:
        df: feature-engineered DataFrame (output of build_features)
        config: dictionary from load_config
    
    Returns:
        trained model
    """
    model_params = config["model"]
    split_date = config["data"]["test_split_date"]

    with mlflow.start_run():
        df["Date"] = pd.to_datetime(df["Date"])

        train_df = df[df["Date"] < split_date]
        test_df = df[df["Date"] >= split_date]

        feature_cols = [
            col for col in df.columns
            if col not in ["Sales", "Date", "Customers"]
        ]

        X_train = train_df[feature_cols]
        y_train = train_df["Sales"]

        X_test = test_df[feature_cols]
        y_test = test_df["Sales"]

        model = RandomForestRegressor(
            n_estimators=model_params["n_estimators"],
            max_depth=model_params["max_depth"],
            random_state=model_params["random_state"],
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        metrics = compute_metrics(y_test, y_pred)

        mlflow.log_params(model_params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "model")

        return model