"""Statistical functions used by the assignment analysis app."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from data_dictionary import SCALE_DEFINITIONS


def score_scale(data: pd.DataFrame, scale_name: str) -> pd.Series:
    """Return a scale total after applying the codebook's reverse scoring."""
    definition = SCALE_DEFINITIONS[scale_name]
    values = data[definition["items"]].apply(pd.to_numeric, errors="coerce").copy()
    for item in definition["reverse"]:
        maximum = _item_maximum(item)
        values[item] = maximum + 1 - values[item]
    return values.sum(axis=1, min_count=len(definition["items"]))


def add_scale_totals(data: pd.DataFrame) -> pd.DataFrame:
    """Add calculated totals without overwriting source columns."""
    result = data.copy()
    for scale_name, definition in SCALE_DEFINITIONS.items():
        if set(definition["items"]).issubset(result.columns):
            result[scale_name] = score_scale(result, scale_name)
    return result


def descriptive_statistics(data: pd.DataFrame, variables: Iterable[str]) -> pd.DataFrame:
    rows = []
    for variable in variables:
        values = pd.to_numeric(data[variable], errors="coerce").dropna()
        if values.empty:
            continue
        rows.append(
            {
                "Variable": variable,
                "N": int(values.size),
                "Missing": int(data[variable].isna().sum()),
                "Minimum": values.min(),
                "Maximum": values.max(),
                "Mean": values.mean(),
                "Std. deviation": values.std(),
                "Skewness": values.skew(),
                "Kurtosis (excess)": values.kurt(),
                "Median": values.median(),
            }
        )
    return pd.DataFrame(rows)


def cronbach_alpha(data: pd.DataFrame, items: list[str], reverse: list[str]) -> tuple[float, pd.DataFrame]:
    """Calculate Cronbach's alpha using reverse-scored item values."""
    values = data[items].apply(pd.to_numeric, errors="coerce").copy()
    for item in reverse:
        values[item] = _item_maximum(item) + 1 - values[item]
    complete = values.dropna()
    item_count = complete.shape[1]
    if item_count < 2 or complete.shape[0] < 2:
        return float("nan"), values
    item_variance = complete.var(axis=0, ddof=1).sum()
    total_variance = complete.sum(axis=1).var(ddof=1)
    alpha = item_count / (item_count - 1) * (1 - item_variance / total_variance)
    return float(alpha), values


def correlation_matrix(data: pd.DataFrame, variables: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    values = data[variables].apply(pd.to_numeric, errors="coerce")
    r = values.corr(method="pearson")
    p = pd.DataFrame(np.nan, index=variables, columns=variables)
    for first in variables:
        for second in variables:
            pair = values[[first, second]].dropna()
            if len(pair) >= 3 and first != second:
                p.loc[first, second] = stats.pearsonr(pair[first], pair[second]).pvalue
            elif first == second:
                p.loc[first, second] = 0.0
    return r, p


def fit_regression(data: pd.DataFrame, dependent: str, predictors: list[str]):
    values = data[[dependent, *predictors]].apply(pd.to_numeric, errors="coerce").dropna()
    if values.empty:
        raise ValueError("There are no complete rows for the selected regression variables.")
    y = values[dependent]
    x = sm.add_constant(values[predictors], has_constant="add")
    return sm.OLS(y, x).fit(), values


def _item_maximum(item: str) -> int:
    if item.startswith(("op", "pn", "pss")):
        return 5
    if item.startswith(("mast", "sest")):
        return 4
    if item.startswith("lifsat"):
        return 7
    if item.startswith("pc"):
        return 5
    if item.startswith("m"):
        return 2
    raise ValueError(f"Unknown item range for {item}")
