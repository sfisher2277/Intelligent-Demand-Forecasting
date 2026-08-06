import pandas as pd


def add_lag_features(df: pd.DataFrame, lag_days: list) -> pd.DataFrame:
    """
    Add lagged sales features, grouped by store.
    
    Args:
        df: DataFrame with Store, Date, Sales columns
        lag_days: list of lag periods to create (e.g. [1, 7])
        
    Returns:
        DataFrame with new lag columns added
    """
    df = df.sort_values(["Store", "Date"])

    for lag in lag_days:
        col_name = f"Sales_lag_{lag}"
        df[col_name] = df.groupby("Store")["Sales"].shift(lag)

    return df


def encode_store_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode the StoreType column.
    
    
    Args:
        df: DataFrame with a StoreType
       
    Returns:
        DataFrame with StoreType replaced by dummy columns
    """
    df = pd.get_dummies(df, columns=["StoreType"], prefix="StoreType")
    return df


def add_holiday_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a simplified binary holiday flag from StateHoliday and SchoolHoliday.
    
    Args:
        df: DataFrame with StateHoliday and SchoolHoliday columns
    
    Returns:
        DATAFrame with new IsHoliday column added
    """
    is_state_holiday = df["StateHoliday"] != "0"
    is_school_holiday = df["SchoolHoliday"] == 1

    df["IsHoliday"] = (is_state_holiday | is_school_holiday).astype(int)
    df = df.drop(columns=["StateHoliday"])

    return df


def build_features(df: pd.DataFrame, lag_days: list) -> pd.DataFrame:
    """
    Apply all feature engineering steps in sequence.
    
    Args:
        df: validated raw DataFrame (output of ingest_data)
        lag_days: list of lag periods for add_lag_features
       
    Returns:
        Dataframe with all engineered features added
    """
    df = add_lag_features(df, lag_days)
    df = encode_store_type(df)
    df = encode_assortment(df)
    df = add_holiday_flags(df)
    df = df.drop(columns=["PromoInterval"])

    return df


def encode_assortment(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode the Assortment column.
    
    Args:
        df: DataFrame with an Assortment column
    
    Returns:
        DataFrame with Assortment replaced by dummy columns
    """
    df = pd.get_dummies(df, columns=["Assortment"], prefix="Assortment")
    return df