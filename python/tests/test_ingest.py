import pandas as pd
import pytest

from src.ingest import validate_schema, merge_store_data, ingest_data


def make_valid_df(n_rows=1000):
    return pd.DataFrame({
        "Store": [1] * n_rows,
        "Sales": [100] * n_rows,
        "Date": ["2015-01-01"] * n_rows,
    })


def test_validate_schema_passes_with_valid_data():
    df = make_valid_df()
    # should not raise
    validate_schema(
        df,
        expected_columns=["Store", "Sales", "Date"],
        critical_cols=["Store", "Sales", "Date"],
        min_rows=100,
    )


def test_validate_schema_raises_on_missing_columns():
    df = make_valid_df()
    with pytest.raises(ValueError, match="Missing expected columns"):
        validate_schema(
            df,
            expected_columns=["Store", "Sales", "Date", "Customers"],
            critical_cols=["Store"],
            min_rows=100,
        )


def test_validate_schema_raises_on_empty_dataframe():
    df = pd.DataFrame(columns=["Store", "Sales", "Date"])
    with pytest.raises(ValueError, match="empty"):
        validate_schema(
            df,
            expected_columns=["Store", "Sales", "Date"],
            critical_cols=["Store"],
            min_rows=0,
        )


def test_validate_schema_raises_on_nulls_in_critical_cols():
    df = make_valid_df()
    df.loc[0, "Sales"] = None
    with pytest.raises(ValueError, match="Unexpected nulls"):
        validate_schema(
            df,
            expected_columns=["Store", "Sales", "Date"],
            critical_cols=["Sales"],
            min_rows=100,
        )


def test_validate_schema_raises_on_too_few_rows():
    df = make_valid_df(n_rows=5)
    with pytest.raises(ValueError, match="Row count suspiciously low"):
        validate_schema(
            df,
            expected_columns=["Store", "Sales", "Date"],
            critical_cols=["Store"],
            min_rows=1000,
        )


def test_merge_store_data_joins_on_store():
    train_df = pd.DataFrame({"Store": [1, 2], "Sales": [100, 200]})
    store_df = pd.DataFrame({"Store": [1, 2], "StoreType": ["a", "b"]})

    merged = merge_store_data(train_df, store_df)

    assert list(merged["StoreType"]) == ["a", "b"]
    assert len(merged) == 2


def test_merge_store_data_keeps_all_train_rows_even_if_store_missing():
    train_df = pd.DataFrame({"Store": [1, 2, 3], "Sales": [100, 200, 300]})
    store_df = pd.DataFrame({"Store": [1, 2], "StoreType": ["a", "b"]})

    merged = merge_store_data(train_df, store_df)

    # left join: all 3 train rows preserved, store 3 gets NaN metadata
    assert len(merged) == 3
    assert pd.isna(merged.loc[merged["Store"] == 3, "StoreType"]).all()


def test_ingest_data_end_to_end(tmp_path):
    train_csv = tmp_path / "train.csv"
    store_csv = tmp_path / "store.csv"

    pd.DataFrame({
        "Store": [1] * 1000,
        "Sales": [100] * 1000,
        "Date": ["2015-01-01"] * 1000,
    }).to_csv(train_csv, index=False)

    pd.DataFrame({"Store": [1], "StoreType": ["a"]}).to_csv(store_csv, index=False)

    df = ingest_data(
        train_path=str(train_csv),
        store_path=str(store_csv),
        expected_columns=["Store", "Sales", "Date", "StoreType"],
        critical_cols=["Store", "Sales"],
        min_rows=500,
    )

    assert len(df) == 1000
    assert "StoreType" in df.columns


def test_ingest_data_raises_when_validation_fails(tmp_path):
    train_csv = tmp_path / "train.csv"
    store_csv = tmp_path / "store.csv"

    # too few rows on purpose
    pd.DataFrame({"Store": [1, 2], "Sales": [100, 200], "Date": ["2015-01-01", "2015-01-02"]}).to_csv(train_csv, index=False)
    pd.DataFrame({"Store": [1, 2], "StoreType": ["a", "b"]}).to_csv(store_csv, index=False)

    with pytest.raises(ValueError, match="Row count suspiciously low"):
        ingest_data(
            train_path=str(train_csv),
            store_path=str(store_csv),
            expected_columns=["Store", "Sales", "Date", "StoreType"],
            critical_cols=["Store"],
            min_rows=1000,
        )