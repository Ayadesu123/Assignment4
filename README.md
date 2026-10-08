# ME2004 Survey Analysis App

An assignment-focused Streamlit application for `ME2004_Survey.sav`.

## Run on Windows

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The application loads the local `ME2004_Survey.sav` automatically. A different `.sav`
file can also be selected in the sidebar.

## Included analyses

- Variable overview and missing-value counts
- Descriptive statistics: N, missing values, minimum, maximum, mean, standard deviation,
  median, skewness, and excess kurtosis
- Histograms and box plots
- Cronbach's alpha for the ten perceived-stress items, including the codebook's reverse
  scoring for `pss4`, `pss5`, `pss7`, and `pss8`
- Pearson correlation coefficients and two-sided p-values
- Multiple linear regression with selectable dependent and independent variables
- Regression coefficients, p-values, confidence intervals, R-squared, adjusted R-squared,
  residual plots, and residual diagnostics
- CSV downloads for report tables and scored data

The tool supports the report but does not replace interpretation of statistical
significance, assumptions, causation limits, or the research question.
