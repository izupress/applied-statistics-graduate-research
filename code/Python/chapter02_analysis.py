from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

dat = pd.read_csv(Path("data/chapter02_student_data.csv"))

missing_table = pd.DataFrame({
    "missing_n": dat.isna().sum(),
    "missing_pct": 100 * dat.isna().mean()
})
print(missing_table.round(1))

format_table = (
    dat["instructional_format"]
    .value_counts(dropna=False)
    .rename_axis("instructional_format")
    .reset_index(name="n")
)
format_table["percent"] = 100 * format_table["n"] / len(dat)
print(format_table.round(1))

completion_table = pd.crosstab(
    dat["instructional_format"],
    dat["completion_status"],
    margins=True,
    dropna=False
)
completion_row_pct = pd.crosstab(
    dat["instructional_format"],
    dat["completion_status"],
    normalize="index",
    dropna=False
) * 100
print(completion_table)
print(completion_row_pct.round(1))

def q1(series):
    return series.quantile(0.25)

def q3(series):
    return series.quantile(0.75)

summary_table = (
    dat.groupby("instructional_format")["exam_score"]
    .agg(
        n_exam="count",
        mean_exam="mean",
        sd_exam="std",
        median_exam="median",
        q1_exam=q1,
        q3_exam=q3,
        min_exam="min",
        max_exam="max",
    )
    .reset_index()
)
print(summary_table.round(1))

fig, ax = plt.subplots()
ax.hist(dat["exam_score"].dropna(), bins=12)
ax.set(xlabel="Examination score", ylabel="Number of students",
       title="Distribution of examination scores")
fig.tight_layout()
plt.show()

groups = [g["exam_score"].dropna().to_numpy()
          for _, g in dat.groupby("instructional_format", sort=True)]
labels = [name for name, _ in dat.groupby("instructional_format", sort=True)]
fig, ax = plt.subplots()
ax.boxplot(groups, labels=labels)
ax.set(xlabel="Instructional format", ylabel="Examination score",
       title="Examination scores by instructional format")
fig.tight_layout()
plt.show()

complete = dat[["study_hours", "exam_score"]].dropna()
fig, ax = plt.subplots()
ax.scatter(complete["study_hours"], complete["exam_score"])
ax.set(xlabel="Weekly study time (hours)", ylabel="Examination score",
       title="Study time and examination performance")
fig.tight_layout()
plt.show()