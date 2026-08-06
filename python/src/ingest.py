import pandas as pd

def load_raw_data(path: str) -> pd.DataFrame:
    """
    Load raw Rossmann data from CSV.
    
    Args:
        path: file path to the CSV
        
    Returns:
        pandas DataFrame of raw data
    """
    df = pd.read_csv(path)
    return df


def validate_schema(
    df: pd.DataFrame,
    expected_columns:list,
    critical_cols: list,
    min_rows: int = 1000
) -> None:
    """
    Validate that the raw data matches expected structure.
    Raises ValueError if validation fails.
    """
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")

    if df.empty:
        raise ValueError("Loaded dataframe is empty")


    for col in critical_cols:
        if df[col].isnull().any():
            raise ValueError(f"Unexpected nulls found in column: {col}")
    
    if len(df) < min_rows:
        raise ValueError(f"Row count suspiciously low: {len(df)} rows (expected at least {min_rows})")


def load_store_data(path: str) -> pd.DataFrame:
    """
    Load store metadata (StoreType, Assortment, etc.) from CSV.
    
    Args:
        path: file path to store.csv
    
    Returns:
        pandas DataFrame of store metadata
    """
    df = pd.read_csv(path)
    return df


def merge_store_data(train_df: pd.DataFrame, store_df: pd.DataFrame) -> pd.DataFrame:
    """
    Join transactional sales data with store metadata.
    
    Args:
        train_df: daily sales data (from train.csv)
        store_df: store-level metadata (from store.csv)
    
    Returns:
        merged DataFrame with store metadata joined in
    """
    merged = train_df.merge(store_df, on="Store", how="left")
    return merged


def ingest_data(
    train_path: str,
    store_path: str,
    expected_columns: list,
    critical_cols: list,
    min_rows: int = 1000
) -> pd.DataFrame:
    """
    Load, join, and validate raw Rossmann data in one step.
    
    Args:
        train_path: file path to train.csv
        store_path: file path to store.csv
        expected_columns: columns that must be present after the join
        critical_cols: columns that must not contain nulls
        min_rows: minimum acceptable row count
    
    Returns:
        validated, merged pandas DataFrame
    """
    train_df = load_raw_data(train_path)
    store_df = load_store_data(store_path)
    df = merge_store_data(train_df, store_df)
    validate_schema(df, expected_columns, critical_cols, min_rows)
    return df