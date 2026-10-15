# Prompt Log

## Prompt 1 – Initial request (plan mode)

I want to build a Streamlit app, `app.py`, that explores correlations between health measures in `nhanes_health.csv`. Read the CSV first. Every numeric column except sex (leave this out of correlations). Save the prompts into prompts.md file.

Your app must include
1. **Data preview.** A short description of the dataset and a table of the rows.
2. **Pairwise view.** Two dropdowns pick X and Y. The app shows a scatter plot, the **correlation r**, and the **number of participants n**. The scatter plot has a trend line or binned means, and an option to color points by a health threshold such as SBP ≥ 130.
3. **Correlation heatmap.** The user picks which numeric variables to include. Every square shows its coefficient, and the color scale is **fixed from −1 to 1**.
4. **Filters.** Sidebar controls for **sex** and an **age range** that update *every* view: the table, scatter plot, r, n and heatmap.
5. **Correlation method.** A toggle between **Pearson** and **Spearman** that applies to both the pairwise view and the heatmap.

## Prompt 2 – Plan approval

Build the app in plan mode. *(Chose "Approve plan, then build"; the approved plan is saved as `plan.md`.)*
