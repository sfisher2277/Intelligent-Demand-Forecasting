import pandas as pd

from src.features import (
    add_lag_features,
    encode_store_type,
    encode_assortment,
    add_holiday_flags,
    build_features,
)


def test_add_lag_features_shifts_within_store():
    df = pd.DataFrame({
        "Store": [1, 1, 1],
        "Date": ["2015-01-01", "2015-01-02", "2015-01-03"],
        "Sales": [100, 200, 300],
    })

    result = add_lag_features(df, lag_days=[1])

    # row 2 (Sales=200) should have yesterday's sales (100) as its lag
    row2 = result[result["Sales"] == 200].iloc[0]
    assert row2["Sales_lag_1"] == 100


def test_add_lag_features_does_not_leak_across_stores():
    # store 1 ends with Sales=999, store 2 starts fresh the next day
    # a broken (non-grouped) shift would leak store 1's last value into store 2's first row
    df = pd.DataFrame({
        "Store": [1, 1, 2, 2],
        "Date": ["2015-01-01", "2015-01-02", "2015-01-01", "2015-01-02"],
        "Sales": [999, 111, 50, 60],
    })

    result = add_lag_features(df, lag_days=[1])

    store2_first_row = result[(result["Store"] == 2) & (result["Sales"] == 50)].iloc[0]
    assert pd.isna(store2_first_row["Sales_lag_1"])


def test_add_lag_features_first_row_per_store_is_nan():
    df = pd.DataFrame({
        "Store": [1, 1],
        "Date": ["2015-01-01", "2015-01-02"],
        "Sales": [100, 200],
    })

    result = add_lag_features(df, lag_days=[1, 7])

    first_row = result[result["Sales"] == 100].iloc[0]
    assert pd.isna(first_row["Sales_lag_1"])
    assert pd.isna(first_row["Sales_lag_7"])


def test_encode_store_type_creates_dummy_columns():
    df = pd.DataFrame({"StoreType": ["a", "b", "c", "d"]})
    result = encode_store_type(df)

    for cat in ["a", "b", "c", "d"]:
        assert f"StoreType_{cat}" in result.columns
    assert "StoreType" not in result.columns


def test_encode_assortment_creates_dummy_columns():
    df = pd.DataFrame({"Assortment": ["a", "b", "c"]})
    result = encode_assortment(df)

    for cat in ["a", "b", "c"]:
        assert f"Assortment_{cat}" in result.columns
    assert "Assortment" not in result.columns


def test_add_holiday_flags_flags_state_holiday():
    df = pd.DataFrame({
        "StateHoliday": ["0", "a"],
        "SchoolHoliday": [0, 0],
    })
    result = add_holiday_flags(df)

    assert list(result["IsHoliday"]) == [0, 1]


def test_add_holiday_flags_flags_school_holiday():
    df = pd.DataFrame({
        "StateHoliday": ["0", "0"],
        "SchoolHoliday": [0, 1],
    })
    result = add_holiday_flags(df)

    assert list(result["IsHoliday"]) == [0, 1]


def test_add_holiday_flags_drops_state_holiday_column():
    df = pd.DataFrame({
        "StateHoliday": ["0"],
        "SchoolHoliday": [0],
    })
    result = add_holiday_flags(df)

    assert "StateHoliday" not in result.columns


def test_build_features_runs_full_pipeline():
    df = pd.DataFrame({
        "Store": [1, 1],
        "Date": ["2015-01-01", "2015-01-02"],
        "Sales": [100, 200],
        "StoreType": ["a", "a"],
        "Assortment": ["a", "a"],
        "StateHoliday": ["0", "0"],
        "SchoolHoliday": [0, 0],
        "PromoInterval": ["Jan,Apr,Jul,Oct", "Jan,Apr,Jul,Oct"],
    })

    result = build_features(df, lag_days=[1])

    assert "Sales_lag_1" in result.columns
    assert "StoreType_a" in result.columns
    assert "Assortment_a" in result.columns
    assert "IsHoliday" in result.columns
    assert "PromoInterval" not in result.columns
    assert "StateHoliday" not in result.columns