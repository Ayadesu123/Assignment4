"""Interactive ME2004 assignment analysis application."""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy import stats

from analysis import (
    add_scale_totals,
    correlation_matrix,
    cronbach_alpha,
    descriptive_statistics,
    fit_regression,
)
from data_dictionary import SCALE_DEFINITIONS, VARIABLE_LABELS

st.set_page_config(page_title="ME2004 Survey Analysis", page_icon="📊", layout="wide")


@st.cache_data(show_spinner=False)
def read_sav(contents: bytes) -> pd.DataFrame:
    import pyreadstat

    data, _ = pyreadstat.read_sav(io.BytesIO(contents), apply_value_formats=False)
    return add_scale_totals(data)


def label(variable: str) -> str:
    return VARIABLE_LABELS.get(variable, variable)


def numeric_variables(data: pd.DataFrame) -> list[str]:
    return [
        column
        for column in data.columns
        if pd.api.types.is_numeric_dtype(data[column]) and data[column].notna().any()
    ]


def download_csv(data: pd.DataFrame, filename: str, label_text: str) -> None:
    st.download_button(
        label_text,
        data=data.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


st.title("ME2004 Survey Analysis")
st.caption("Assignment-focused exploratory data analysis, reliability, correlations, and multiple regression")

with st.sidebar:
    st.header("1. Load data")
    uploaded = st.file_uploader("Choose the SPSS survey file", type=["sav"])
    default_path = Path(__file__).with_name("ME2004_Survey.sav")
    if uploaded is not None:
        data = read_sav(uploaded.getvalue())
        source_name = uploaded.name
    elif default_path.exists():
        data = read_sav(default_path.read_bytes())
        source_name = default_path.name
    else:
        data = None
        source_name = ""
    st.divider()
    st.markdown("**Codebook scoring is applied automatically**")
    st.caption("Reverse-scored items are used when calculated totals are created. Source item columns remain unchanged.")

if data is None:
    st.info("Upload `ME2004_Survey.sav` to begin.")
    st.stop()

st.success(f"Loaded {source_name}: {len(data):,} cases and {len(data.columns):,} variables.")
tabs = st.tabs(["Overview", "Part A: EDA", "Reliability", "Part B: Correlations", "Part C: Regression", "Data"])

with tabs[0]:
    st.subheader("Dataset overview")
    a, b, c = st.columns(3)
    a.metric("Cases", f"{len(data):,}")
    b.metric("Variables", f"{len(data.columns):,}")
    c.metric("Calculated totals", sum(column in data for column in SCALE_DEFINITIONS))
    st.markdown(
        "Use this tool to support the report, not replace interpretation. Results should be "
        "reported with the research question, assumptions, limitations, and appropriate course references."
    )
    overview = pd.DataFrame(
        {
            "Variable": data.columns,
            "Label": [label(column) for column in data.columns],
            "Type": [str(data[column].dtype) for column in data.columns],
            "Missing": [int(data[column].isna().sum()) for column in data.columns],
            "Unique values": [int(data[column].nunique(dropna=True)) for column in data.columns],
        }
    )
    st.dataframe(overview, use_container_width=True, hide_index=True)
    download_csv(overview, "variable_overview.csv", "Download variable overview")

with tabs[1]:
    st.subheader("Part A — Exploratory data analysis")
    available = numeric_variables(data)
    selected = st.multiselect(
        "Select numeric variables for descriptive statistics and plots",
        available,
        default=[v for v in ["Tpstress", "Toptim", "Tmast", "Tlifesat", "Tslfest", "Tpcoiss"] if v in available],
        format_func=label,
    )
    if selected:
        summary = descriptive_statistics(data, selected)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        download_csv(summary, "descriptive_statistics.csv", "Download descriptive statistics")
        plot_variable = st.selectbox("Variable to plot", selected, format_func=label)
        chart_type = st.radio("Plot type", ["Histogram", "Box plot"], horizontal=True)
        fig, ax = plt.subplots(figsize=(9, 4))
        values = pd.to_numeric(data[plot_variable], errors="coerce").dropna()
        if chart_type == "Histogram":
            sns.histplot(values, kde=True, ax=ax, color="#2563eb")
            ax.set_ylabel("Frequency")
        else:
            sns.boxplot(x=values, ax=ax, color="#93c5fd")
            ax.set_xlabel(label(plot_variable))
        ax.set_title(f"{chart_type}: {label(plot_variable)}")
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Select at least one numeric variable.")

with tabs[2]:
    st.subheader("Reliability test — Total perceived stress")
    stress_items = SCALE_DEFINITIONS["Tpstress"]["items"]
    if set(stress_items).issubset(data.columns):
        alpha, scored = cronbach_alpha(data, stress_items, SCALE_DEFINITIONS["Tpstress"]["reverse"])
        st.metric("Cronbach's alpha", "Not available" if pd.isna(alpha) else f"{alpha:.3f}")
        st.write(
            "Cronbach's alpha estimates internal consistency across the ten perceived-stress items. "
            "The calculation uses reverse-scored items pss4, pss5, pss7, and pss8 and complete cases."
        )
        item_table = pd.DataFrame(
            {
                "Item": stress_items,
                "Reverse scored": ["Yes" if item in SCALE_DEFINITIONS["Tpstress"]["reverse"] else "No" for item in stress_items],
                "Mean after scoring": [scored[item].mean() for item in stress_items],
                "Std. deviation": [scored[item].std() for item in stress_items],
            }
        )
        st.dataframe(item_table, use_container_width=True, hide_index=True)
        download_csv(item_table, "perceived_stress_reliability_items.csv", "Download reliability item table")

with tabs[3]:
    st.subheader("Part B — Pearson correlations")
    available = numeric_variables(data)
    selected = st.multiselect(
        "Select variables for the correlation matrix",
        available,
        default=[v for v in ["Tpstress", "Toptim", "Tmast", "Tnegaff", "Tlifesat", "Tslfest"] if v in available],
        format_func=label,
        key="correlation_variables",
    )
    if len(selected) >= 2:
        r, p = correlation_matrix(data, selected)
        st.markdown("**Pearson r**")
        st.dataframe(r.style.format("{:.3f}"), use_container_width=True)
        st.markdown("**Two-sided p-values**")
        st.dataframe(p.style.format("{:.4f}"), use_container_width=True)
        st.caption("Correlation describes association, not causation. Values close to ±1 are stronger; values near 0 are weaker.")
        download_csv(r.reset_index().rename(columns={"index": "Variable"}), "correlation_matrix.csv", "Download correlation matrix")
    else:
        st.info("Select at least two numeric variables.")

with tabs[4]:
    st.subheader("Part C — Multiple linear regression")
    available = numeric_variables(data)
    dependent = st.selectbox("Dependent variable", available, index=available.index("Tpstress") if "Tpstress" in available else 0, format_func=label)
    candidates = [v for v in available if v != dependent]
    predictors = st.multiselect(
        "Independent variables",
        candidates,
        default=[v for v in ["Toptim", "Tmast", "Tnegaff", "Tlifesat", "Tslfest", "Tpcoiss"] if v in candidates],
        format_func=label,
    )
    if predictors:
        try:
            model, used_data = fit_regression(data, dependent, predictors)
            left, middle, right = st.columns(3)
            left.metric("R²", f"{model.rsquared:.3f}")
            middle.metric("Adjusted R²", f"{model.rsquared_adj:.3f}")
            right.metric("Complete cases", f"{len(used_data):,}")
            coefficients = pd.DataFrame(
                {
                    "Term": model.params.index,
                    "Coefficient": model.params.values,
                    "Std. error": model.bse.values,
                    "t": model.tvalues.values,
                    "p-value": model.pvalues.values,
                    "95% CI lower": model.conf_int()[0].values,
                    "95% CI upper": model.conf_int()[1].values,
                }
            )
            st.dataframe(coefficients.style.format({column: "{:.4f}" for column in coefficients.columns if column != "Term"}), use_container_width=True, hide_index=True)
            st.write(f"Overall model F-test p-value: **{model.f_pvalue:.4g}**")
            st.caption("Interpret coefficients while holding the other selected predictors constant. Statistical significance does not establish causality.")
            download_csv(coefficients, "regression_coefficients.csv", "Download regression coefficients")

            residuals = model.resid
            fitted = model.fittedvalues
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))
            sns.scatterplot(x=fitted, y=residuals, ax=axes[0], color="#2563eb")
            axes[0].axhline(0, color="black", linestyle="--")
            axes[0].set(xlabel="Predicted values", ylabel="Residuals", title="Residuals vs predicted")
            sns.histplot(residuals, kde=True, ax=axes[1], color="#16a34a")
            axes[1].set(title="Residual distribution", xlabel="Residual")
            st.pyplot(fig, clear_figure=True)
            st.markdown("**Diagnostics**")
            st.write(
                f"Residual skewness: `{stats.skew(residuals):.3f}`; "
                f"residual excess kurtosis: `{stats.kurtosis(residuals):.3f}`. "
                "Inspect both plots for non-linearity, unequal spread, and unusual observations."
            )
        except (ValueError, KeyError) as error:
            st.error(str(error))
    else:
        st.info("Select at least one independent variable.")

with tabs[5]:
    st.subheader("Data viewer")
    st.caption("Calculated scale totals are included for analysis. Use the row and column controls to inspect the imported data.")
    st.dataframe(data, use_container_width=True, height=520)
    download_csv(data, "me2004_scored_data.csv", "Download scored data as CSV")
