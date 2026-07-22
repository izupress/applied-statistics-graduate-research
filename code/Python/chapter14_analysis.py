import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm, AnovaRM

anc = pd.read_csv("data/chapter14_ancova.csv")
anc["group"] = pd.Categorical(anc["group"],
    categories=["Control","Workshop","Blended"])
model = smf.ols(
    "post_score ~ baseline_score + group",
    data=anc
).fit(cov_type="HC3")
print(model.summary())

reduced = smf.ols(
    "post_score ~ baseline_score + group",
    data=anc
).fit()
expanded = smf.ols(
    "post_score ~ baseline_score * group",
    data=anc
).fit()
print(anova_lm(reduced, expanded))

long = pd.read_csv("data/chapter14_longitudinal.csv")
long["time"] = pd.Categorical(long["time"],
    categories=["Baseline","Post","Follow-up"], ordered=True)
long["treatment"] = pd.Categorical(long["treatment"],
    categories=["Control","Intervention"])
obs = long.dropna(subset=["outcome_score"])
count = obs.groupby("student_id").time.nunique()
balanced = obs[obs.student_id.isin(count[count==3].index)]

print(AnovaRM(
    balanced,
    depvar="outcome_score",
    subject="student_id",
    within=["time"]
).fit())

mixed = smf.mixedlm(
    "outcome_score ~ time_num * treatment + I(time_num ** 2) + prior_score",
    obs,
    groups=obs["student_id"],
    re_formula="~time_num"
).fit(reml=True, method="lbfgs")
print(mixed.summary())