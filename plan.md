# Plan: Health Correlation Explorer (`app.py`)

## Context
CAI5735 M9 exercise ([M9 Exercise - Health Correlation App.md](CAI5735_M9/M9 Exercise - Health Correlation App.md)). Build a single-file Streamlit app that explores correlations in `nhanes_health.csv`, then log the prompts and the approved plan. The folder holds `nhanes_health.csv`, an empty `prompts.md` and an empty `verification.md`.

**What the CSV contains** (checked): 4,433 rows and 11 columns. `sex` is text (Female 2263 / Male 2170). The other 10 are numeric: `age, bmi, waist_cm, systolic_bp, diastolic_bp, hba1c, total_chol, hdl_chol, sleep_hours, sedentary_minutes`. **No column has missing values**, but the app still handles NaNs, so it stays correct if the data changes.

## Files
- `prompts.md`: write the user's first message (intro + pasted requirements) as entry 1, under a heading such as "## Prompt 1 – Initial request (plan mode)". Add later prompts as they come in.
- `plan.md`: save a copy of this plan after approval (the exercise requires it).
- `app.py`: the app.
- `requirements.txt`: `streamlit`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy` (needed later for deployment).

Packages used: streamlit, pandas, numpy, matplotlib, seaborn, scipy. pandas needs scipy for Spearman. No plotly and no other extras. These match the course run command.

## app.py structure (build in this order)
1. **Load**: `@st.cache_data def load_data()` → `pd.read_csv("nhanes_health.csv")` (relative path). `NUMERIC_COLS = df.select_dtypes("number").columns` (this leaves out `sex`). A `LABELS` dict maps each column to a readable name and unit, taken from the data dictionary.
2. **Sidebar filters → one `filtered` DataFrame**:
   - Sex: `st.radio` with All / Female / Male.
   - Age range: `st.slider` from the data's min to max (20–80), default is the full range. A caption notes that "80 = 80+".
   - Method: `st.radio` with Pearson / Spearman, stored as `method = "pearson"|"spearman"`.
   - `filtered = df[sex_mask & df.age.between(lo, hi)]`. **Every view below uses only `filtered` and `method`**. Nothing reads `df` directly after this point. If `len(filtered) < 3`, show a warning and stop.
3. **Data preview**: a short markdown description (NHANES 2017–18, adults 20+, one row per participant, the sample is not the US population). Metrics show the number of rows shown and the active filters. `st.dataframe(filtered)`. A data dictionary sits in an expander.
4. **Pairwise view**:
   - Two `st.selectbox` controls for X and Y from `NUMERIC_COLS`. Defaults are `age` and `systolic_bp`. Warn if X == Y.
   - `pair = filtered[[x, y]].dropna()`. Then `n = len(pair)` and `r = pair[x].corr(pair[y], method=method)`. Show both with `st.metric` as "Pearson r" or "Spearman ρ", plus n.
   - Color option: a selectbox with "None" plus fixed thresholds: SBP ≥ 130, DBP ≥ 80, BMI ≥ 30, HbA1c ≥ 6.5, Total chol ≥ 240. Points are colored "at/above" vs "below". Any threshold can be applied to any X/Y pair.
   - Plot (matplotlib/seaborn): scatter with alpha ≈ 0.3 and small points. Overlay a **binned-means line** made from X quantile bins (about 10, using `pd.qcut` with `duplicates="drop"`) that plots the mean Y per bin. A checkbox adds an OLS trend line from `np.polyfit`. Binned means are the default because they show non-linear shapes such as the U-shaped sleep curve.
   - A caption gives the cautions: r ≈ 0 does not mean no relationship, Spearman measures a monotonic relationship, and correlation is not causation.
5. **Heatmap**:
   - `st.multiselect` of `NUMERIC_COLS`, default all. Require ≥ 2.
   - `corr = filtered[cols].corr(method=method)`. pandas drops missing values pair by pair, so it matches the pairwise view.
   - `sns.heatmap(corr, annot=True, fmt=".2f", vmin=-1, vmax=1, center=0, cmap="RdBu_r", square=True)`. The **scale is fixed from −1 to 1**. Every cell has an annotation.
   - n shown next to r: a caption says "n = {len(filtered)} participants". For safety, also compute a pairwise-n matrix (`notna().T @ notna()`). If its counts differ, show it in an expander. Otherwise say "all pairs use n = …".
6. A footer notes that the method and filters apply to every view.

## Verification
- Run: `uv run --with streamlit,pandas,seaborn,scipy streamlit run app.py` and check that the page loads.
- A separate pandas check in the terminal for the `verification.md` rows: all participants, `age`–`systolic_bp`, `bmi`–`waist_cm`, `waist_cm`–`hdl_chol`; then Female and Male only for `age`–`systolic_bp` (r and n). Compare the results with what the app shows, then confirm that the Female heatmap cell matches the pairwise r. The user fills in `verification.md`, since the exercise asks them to compute it themselves.
- Switch to Spearman and confirm that the r and the heatmap both change. Narrow the age range and confirm that the table, n, r and heatmap all update.

## Open questions / assumptions
- The sex filter uses "All / Female / Male" (one choice) instead of a multiselect.
- The threshold list is fixed, not a free-entry box with a custom variable and cutoff.
