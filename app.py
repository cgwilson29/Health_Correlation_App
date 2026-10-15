"""Health Correlation Explorer: NHANES 2017-2018 adults (CAI5735 M9)."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Health Correlation Explorer", layout="wide")

LABELS = {
    "age": "Age (years)",
    "bmi": "BMI (kg/m²)",
    "waist_cm": "Waist circumference (cm)",
    "systolic_bp": "Systolic BP (mmHg)",
    "diastolic_bp": "Diastolic BP (mmHg)",
    "hba1c": "HbA1c (%)",
    "total_chol": "Total cholesterol (mg/dL)",
    "hdl_chol": "HDL cholesterol (mg/dL)",
    "sleep_hours": "Sleep on workdays (hours)",
    "sedentary_minutes": "Sedentary time (min/day)",
}

# Health thresholds for coloring the scatter plot: label -> (column, cutoff)
THRESHOLDS = {
    "Systolic BP ≥ 130 (high BP)": ("systolic_bp", 130),
    "Diastolic BP ≥ 80 (high BP)": ("diastolic_bp", 80),
    "BMI ≥ 30 (obesity)": ("bmi", 30),
    "HbA1c ≥ 6.5 (diabetes)": ("hba1c", 6.5),
    "Total cholesterol ≥ 240 (high)": ("total_chol", 240),
}


@st.cache_data
def load_data():
    return pd.read_csv("nhanes_health.csv")


def label(col):
    return LABELS.get(col, col)


df = load_data()
# Numeric columns only, so `sex` (text) never enters a correlation
NUMERIC_COLS = df.select_dtypes("number").columns.tolist()

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Filters")
sex_choice = st.sidebar.radio("Sex", ["All", "Female", "Male"])
age_min, age_max = int(df["age"].min()), int(df["age"].max())
age_lo, age_hi = st.sidebar.slider(
    "Age range", age_min, age_max, (age_min, age_max)
)
st.sidebar.caption("Age 80 means 80 or older.")

st.sidebar.header("Correlation method")
method_label = st.sidebar.radio("Method", ["Pearson", "Spearman"])
method = method_label.lower()
r_symbol = "r" if method == "pearson" else "ρ"

# One filtered frame feeds every view below
mask = df["age"].between(age_lo, age_hi)
if sex_choice != "All":
    mask &= df["sex"] == sex_choice
filtered = df[mask]

st.sidebar.markdown("---")
st.sidebar.metric("Participants after filters", f"{len(filtered):,}")

st.title("Health Correlation Explorer")

if len(filtered) < 3:
    st.warning("Fewer than 3 participants match these filters. Widen the filters.")
    st.stop()

filter_text = f"Sex: **{sex_choice}** · Age: **{age_lo}–{age_hi}** · Method: **{method_label}**"

# ---------------------------------------------------------------- 1. data preview
st.header("1. Data preview")
st.markdown(
    "Each row is one adult (age 20+) from the CDC's 2017–2018 **National Health and "
    "Nutrition Examination Survey (NHANES)**. The data hold body measurements, blood "
    "pressure, blood tests (HbA1c, cholesterol) and self-reported sleep and sitting time. "
    "NHANES oversamples some groups, so these correlations describe *this sample*, "
    "not the US population."
)
st.markdown(filter_text)
st.caption(f"Showing {len(filtered):,} of {len(df):,} participants.")
st.dataframe(filtered, width="stretch", height=300)
with st.expander("Data dictionary"):
    st.table(
        pd.DataFrame(
            {"Column": list(LABELS), "Meaning (units)": list(LABELS.values())}
        ).set_index("Column")
    )

# ---------------------------------------------------------------- 2. pairwise view
st.header("2. Pairwise view")
c1, c2, c3 = st.columns(3)
x = c1.selectbox("X variable", NUMERIC_COLS, index=NUMERIC_COLS.index("age"), format_func=label)
y = c2.selectbox("Y variable", NUMERIC_COLS, index=NUMERIC_COLS.index("systolic_bp"), format_func=label)
color_by = c3.selectbox("Color points by", ["None"] + list(THRESHOLDS))

if x == y:
    st.warning("Pick two different variables.")
else:
    pair_cols = [x, y]
    if color_by != "None":
        thr_col, cutoff = THRESHOLDS[color_by]
        pair_cols = list(dict.fromkeys(pair_cols + [thr_col]))
    pair = filtered[pair_cols].dropna(subset=[x, y])
    n = len(pair)
    r = pair[x].corr(pair[y], method=method) if n >= 3 else np.nan

    m1, m2, m3 = st.columns(3)
    m1.metric(f"{method_label} {r_symbol}", "—" if np.isnan(r) else f"{r:.3f}")
    m2.metric("Participants (n)", f"{n:,}")
    m3.markdown(filter_text)

    show_bins = st.checkbox("Show binned means", value=True)
    show_ols = st.checkbox("Show linear trend line", value=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    if color_by == "None":
        ax.scatter(pair[x], pair[y], s=10, alpha=0.3, color="tab:blue", label="Participants")
    else:
        above = pair[thr_col] >= cutoff
        ax.scatter(pair.loc[~above, x], pair.loc[~above, y], s=10, alpha=0.3,
                   color="tab:blue", label=f"Below ({(~above).sum():,})")
        ax.scatter(pair.loc[above, x], pair.loc[above, y], s=10, alpha=0.45,
                   color="tab:red", label=f"{color_by} ({above.sum():,})")

    if show_bins and n >= 10:
        bins = pd.qcut(pair[x], q=10, duplicates="drop")
        binned = pair.groupby(bins, observed=True).agg(xm=(x, "mean"), ym=(y, "mean"))
        ax.plot(binned["xm"], binned["ym"], "-o", color="black", lw=2, ms=6,
                label="Binned means (deciles of X)")
    if show_ols and n >= 3:
        slope, intercept = np.polyfit(pair[x], pair[y], 1)
        xs = np.linspace(pair[x].min(), pair[x].max(), 100)
        ax.plot(xs, slope * xs + intercept, "--", color="darkorange", lw=2, label="Linear fit")

    ax.set_xlabel(label(x))
    ax.set_ylabel(label(y))
    ax.set_title(f"{label(y)} vs {label(x)}   ({method_label} {r_symbol} = {r:.2f}, n = {n:,})")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Cautions: an r near 0 does not mean *no relationship*. A U-shaped pattern "
        "(e.g. sleep hours) can give r ≈ 0, so check the binned means. Pearson measures "
        "linear association; Spearman measures monotonic (rank) association. "
        "Correlation is not causation."
    )

# ---------------------------------------------------------------- 3. heatmap
st.header("3. Correlation heatmap")
heat_cols = st.multiselect(
    "Variables to include", NUMERIC_COLS, default=NUMERIC_COLS, format_func=label
)

if len(heat_cols) < 2:
    st.info("Pick at least two variables.")
else:
    sub = filtered[heat_cols]
    corr = sub.corr(method=method)  # pairwise-complete, same as the pairwise view
    notna = sub.notna().astype(int)
    pair_n = notna.T @ notna

    st.markdown(filter_text)
    if pair_n.values.min() == pair_n.values.max():
        st.markdown(f"Every coefficient uses **n = {int(pair_n.values.min()):,}** participants.")
    else:
        st.markdown(
            f"n per pair ranges from **{int(pair_n.values.min()):,}** to "
            f"**{int(pair_n.values.max()):,}** (see the table below)."
        )

    size = max(6, 0.8 * len(heat_cols) + 2)
    fig, ax = plt.subplots(figsize=(size, size * 0.8))
    sns.heatmap(
        corr, annot=True, fmt=".2f", vmin=-1, vmax=1, center=0, cmap="RdBu_r",
        square=True, linewidths=0.5, cbar_kws={"label": f"{method_label} {r_symbol}"},
        annot_kws={"size": 8}, ax=ax,
    )
    ax.set_title(f"{method_label} correlations (n = {len(filtered):,}; color scale fixed −1 to 1)")
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("Participants (n) per pair"):
        st.dataframe(pair_n)

st.markdown("---")
st.caption(
    "The sex and age filters and the correlation method apply to every view above: "
    "the table, scatter plot, r, n and heatmap."
)
