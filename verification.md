
| # | Check | App shows | pandas gives | Match? |
|---|---|---|---|---|
| 1 | r for `age` vs `systolic_bp`, all participants |0.463 |0.463 | yes|
| 2 | r for `bmi` vs `waist_cm`, all participants |0.903 |0.903 | yes|
| 3 | r for `waist_cm` vs `hdl_chol`, all participants |-0.335 |-0.335 | yes|
| 4 | r and n for `age` vs `systolic_bp`, **Female only** |r = 0.555; n = 2,263 | r = 0.555, n = 2263|yes |
| 5 | r and n for `age` vs `systolic_bp`, **Male only** |r = 0.351; n = 2,170 | r = 0.351, n = 2170 |yes|
| 6 | With the filter set to Female, does the heatmap's `age`/`systolic_bp` square match row 4?  |0.56 (yes) | 0.56 (yes) |yes |

#Notebook Cautions
#Keep the two cautions from the M9 notebook in mind:
- An r near zero does not mean "no relationship" (remember the U-shaped sleep curve).
- A heatmap is only honest if its colors run from −1 to 1.

#Verification Code used in Marimo Notebook:  
import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    df = pd.read_csv("nhanes_health.csv")
    return df, pd


@app.cell
def _(df):
    df["age"].corr(df["systolic_bp"])
    return


@app.cell
def _(df):
    df["bmi"].corr(df["waist_cm"])
    return


@app.cell
def _(df):
    df["waist_cm"].corr(df["hdl_chol"])
    return


@app.cell
def _(df):
    f = df[(df["sex"] == "Female")]
    f["age"].corr(f["systolic_bp"]), len(f)
    return


@app.cell
def _(df):
    m = df[(df["sex"] == "Male")]
    m["age"].corr(m["systolic_bp"]), len(m)
    return


@app.cell
def _(pd):
    df_check = pd.read_csv("nhanes_health.csv")
    fem = df_check[df_check["sex"] == "Female"]

    # Same matrix the app's heatmap uses: every numeric column (sex is text, so it drops out)
    fem_corr = fem.select_dtypes("number").corr(method="pearson")
    fem_corr.round(2)

    heat_r = fem_corr.loc["age", "systolic_bp"]
    pair_r = fem["age"].corr(fem["systolic_bp"])
    n_fem = len(fem)

    {
        "heatmap square (2 dp)": round(heat_r, 2),
        "heatmap square (full)": heat_r,
        "pairwise r (row 4)": round(pair_r, 3),
        "n": n_fem,
        "match": abs(heat_r - pair_r) < 1e-12,
    }

    return


if __name__ == "__main__":
    app.run()
