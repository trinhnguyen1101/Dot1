import os
import re
import pandas as pd

BASE_DIR = r"d:\rawdata\Dot1"
RAW_DIR = os.path.join(BASE_DIR, "raw_data")
CLEAN_DIR = os.path.join(BASE_DIR, "cleaned_data")
DROP_DIR = os.path.join(CLEAN_DIR, "data_dropped")

START_YEAR = 1990
END_YEAR = 2024
MISSINGNESS_THRESHOLD = 0.50

VNM_FILE = os.path.join(RAW_DIR, "VNM_macro_data.csv")

DERIVED_COLUMNS = {
    "Trade_Balance_USD": ("Exports_USD", "Imports_USD"),
    "GDP_Per_Capita_USD": ("GDP_Current_USD", "Population"),
    "GDP_GNI_Gap_Pct": ("GDP_Current_USD", "GNI_USD"),
    "Economic_Openness_Pct": ("Exports_USD", "Imports_USD", "GDP_Current_USD"),
    "FDI_to_GDP_Pct": ("FDI_Inflows_USD", "GDP_Current_USD"),
    "Labor_Participation_Rate_Pct": ("Labor_Force_Total", "Population"),
}

DATA_DICTIONARY = {
    "FDI_Inflows_USD": "Foreign direct investment, net inflows (current USD)",
    "Remittances_Pct_GDP": "Personal remittances, received (% of GDP)",
    "Inflation_CPI_Pct": "Inflation, consumer prices (annual %)",
    "Lending_Interest_Rate_Pct": "Lending interest rate (%)",
    "Exports_USD": "Exports of goods and services (current USD)",
    "Imports_USD": "Imports of goods and services (current USD)",
    "GDP_Growth_Pct": "GDP growth (annual %)",
    "Unemployment_Pct": "Unemployment, total (% of total labor force)",
    "Population": "Population, total",
    "GNI_USD": "GNI (current USD)",
    "GDP_Current_USD": "GDP (current USD)",
    "Labor_Force_Total": "Labor force, total",
    "Trade_Balance_USD": "Exports minus imports (current USD)",
    "GDP_Per_Capita_USD": "GDP per capita (current USD)",
    "GDP_GNI_Gap_Pct": "(GDP - GNI) / GDP * 100",
    "Economic_Openness_Pct": "(Exports + Imports) / GDP * 100",
    "FDI_to_GDP_Pct": "FDI inflows / GDP * 100",
    "Labor_Participation_Rate_Pct": "Labor force / population * 100",
}

IMPUTE_MEAN_COLUMNS = [
    "Lending_Interest_Rate_Pct",
    "Remittances_Pct_GDP",
    "Unemployment_Pct",
    "Inflation_CPI_Pct",
]


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def load_reference_columns() -> list:
    df = pd.read_csv(VNM_FILE)
    return list(df.columns)


def extract_country_code(filename: str) -> str:
    match = re.match(r"([A-Z]{3})_macro_data\.csv", filename)
    if not match:
        return "UNK"
    return match.group(1)


def standardize_columns(df: pd.DataFrame, ref_cols: list) -> pd.DataFrame:
    for col in ref_cols:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[ref_cols]
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    for col in df.columns:
        if col == "Year":
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def filter_years(df: pd.DataFrame) -> pd.DataFrame:
    if "Year" not in df.columns:
        return df
    return df[(df["Year"] >= START_YEAR) & (df["Year"] <= END_YEAR)].copy()


def recompute_derived(df: pd.DataFrame, keep_cols: list) -> pd.DataFrame:
    if "Trade_Balance_USD" in keep_cols:
        if "Exports_USD" in df.columns and "Imports_USD" in df.columns:
            df["Trade_Balance_USD"] = df["Exports_USD"] - df["Imports_USD"]

    if "GDP_Per_Capita_USD" in keep_cols:
        if "GDP_Current_USD" in df.columns and "Population" in df.columns:
            df["GDP_Per_Capita_USD"] = df["GDP_Current_USD"] / df["Population"]

    if "GDP_GNI_Gap_Pct" in keep_cols:
        if "GDP_Current_USD" in df.columns and "GNI_USD" in df.columns:
            df["GDP_GNI_Gap_Pct"] = ((df["GDP_Current_USD"] - df["GNI_USD"]) / df["GDP_Current_USD"]) * 100

    if "Economic_Openness_Pct" in keep_cols:
        if "Exports_USD" in df.columns and "Imports_USD" in df.columns and "GDP_Current_USD" in df.columns:
            df["Economic_Openness_Pct"] = ((df["Exports_USD"] + df["Imports_USD"]) / df["GDP_Current_USD"]) * 100

    if "FDI_to_GDP_Pct" in keep_cols:
        if "FDI_Inflows_USD" in df.columns and "GDP_Current_USD" in df.columns:
            df["FDI_to_GDP_Pct"] = (df["FDI_Inflows_USD"] / df["GDP_Current_USD"]) * 100

    if "Labor_Participation_Rate_Pct" in keep_cols:
        if "Labor_Force_Total" in df.columns and "Population" in df.columns:
            df["Labor_Participation_Rate_Pct"] = (df["Labor_Force_Total"] / df["Population"]) * 100

    return df


def impute_mean_by_country(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        if col not in df.columns:
            continue
        country_means = df.groupby("Country")[col].transform("mean")
        df[col] = df[col].fillna(country_means)
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mean())
    return df


def main() -> None:
    ensure_dir(CLEAN_DIR)
    ensure_dir(DROP_DIR)
    ref_cols = load_reference_columns()

    country_frames = {}
    raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith("_macro_data.csv")]

    years_outside_range = set()

    for filename in raw_files:
        country_code = extract_country_code(filename)
        path = os.path.join(RAW_DIR, filename)
        df = pd.read_csv(path)
        df = standardize_columns(df, ref_cols)
        df = coerce_types(df)
        if "Year" in df.columns:
            years_all = df["Year"].dropna().astype(int)
            years_outside_range.update(years_all[(years_all < START_YEAR) | (years_all > END_YEAR)].tolist())
        df = filter_years(df)
        df.insert(0, "Country", country_code)
        country_frames[country_code] = df

    panel = pd.concat(country_frames.values(), ignore_index=True)

    indicator_cols = [c for c in panel.columns if c not in ("Country", "Year")]
    missing_by_col = panel[indicator_cols].isna().mean().sort_values(ascending=False)
    cols_to_drop = missing_by_col[missing_by_col > MISSINGNESS_THRESHOLD].index.tolist()

    keep_cols = [c for c in indicator_cols if c not in cols_to_drop]

    panel = panel[["Country", "Year"] + keep_cols]

    missing_by_year = (
        panel.groupby("Year")[keep_cols]
        .apply(lambda d: d.isna().mean().mean())
        .sort_index()
    )
    years_to_drop = missing_by_year[missing_by_year > MISSINGNESS_THRESHOLD].index.tolist()

    if years_to_drop:
        panel = panel[~panel["Year"].isin(years_to_drop)].copy()

    impute_cols = [c for c in IMPUTE_MEAN_COLUMNS if c in keep_cols]
    if impute_cols:
        panel = impute_mean_by_country(panel, impute_cols)

    panel = recompute_derived(panel, keep_cols)

    panel = panel.sort_values(["Country", "Year"], ascending=[True, True])

    panel_output = os.path.join(CLEAN_DIR, "panel_macro_cleaned.csv")
    panel.to_csv(panel_output, index=False)

    for country_code in country_frames.keys():
        country_df = panel[panel["Country"] == country_code].drop(columns=["Country"])
        country_output = os.path.join(CLEAN_DIR, f"{country_code}_macro_cleaned.csv")
        country_df.to_csv(country_output, index=False)

    missing_cols_output = os.path.join(DROP_DIR, "missingness_columns.csv")
    missing_by_col.to_csv(missing_cols_output, header=["missing_share"])

    missing_years_output = os.path.join(DROP_DIR, "missingness_years.csv")
    missing_by_year.to_csv(missing_years_output, header=["missing_share"])

    dictionary_output = os.path.join(DROP_DIR, "data_dictionary.csv")
    dictionary_rows = []

    dictionary_rows.append(
        {
            "column": "__RULE__TIME_RANGE__",
            "description": f"Kept years {START_YEAR}-{END_YEAR}; removed years outside this range.",
        }
    )
    dictionary_rows.append(
        {
            "column": "__RULE__MISSINGNESS__",
            "description": f"Dropped columns/years with missing_share > {MISSINGNESS_THRESHOLD:.2f}.",
        }
    )
    dictionary_rows.append(
        {
            "column": "__RULE__IMPUTE_MEAN__",
            "description": "Filled missing values using per-country mean, then global mean if still missing.",
        }
    )

    dropped_cols_summary = ", ".join(cols_to_drop) if cols_to_drop else "None"
    dictionary_rows.append(
        {
            "column": "__DROPPED_COLUMNS__",
            "description": dropped_cols_summary,
        }
    )

    dropped_years_missing = ", ".join(str(y) for y in years_to_drop) if years_to_drop else "None"
    dictionary_rows.append(
        {
            "column": "__DROPPED_YEARS_MISSINGNESS__",
            "description": dropped_years_missing,
        }
    )

    dropped_years_range = ", ".join(str(y) for y in sorted(years_outside_range)) if years_outside_range else "None"
    dictionary_rows.append(
        {
            "column": "__DROPPED_YEARS_TIME_RANGE__",
            "description": dropped_years_range,
        }
    )

    imputed_cols_summary = ", ".join(impute_cols) if impute_cols else "None"
    dictionary_rows.append(
        {
            "column": "__IMPUTED_COLUMNS__",
            "description": imputed_cols_summary,
        }
    )

    for col in cols_to_drop:
        dictionary_rows.append(
            {
                "column": f"__DROPPED_COLUMN__:{col}",
                "description": f"missing_share={missing_by_col[col]:.6f}",
            }
        )

    for year in years_to_drop:
        dictionary_rows.append(
            {
                "column": f"__DROPPED_YEAR__:{year}",
                "description": f"missing_share={missing_by_year.loc[year]:.6f}",
            }
        )

    for col in ["Year"] + keep_cols:
        dictionary_rows.append({"column": col, "description": DATA_DICTIONARY.get(col, "")})
    pd.DataFrame(dictionary_rows).to_csv(dictionary_output, index=False)

    print("Cleaned panel saved to:", panel_output)
    print("Missingness by column saved to:", missing_cols_output)
    print("Missingness by year saved to:", missing_years_output)
    print("Data dictionary saved to:", dictionary_output)


if __name__ == "__main__":
    main()
