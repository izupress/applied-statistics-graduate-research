# Chapter 17: confirmatory factor analysis.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "lavaan", "semTools", "dplyr"
# ))

library(lavaan)
library(semTools)
library(dplyr)

data <- read.csv(
  "data/chapter17_cfa_validation.csv"
)

items <- c(
  "q1","q2","q3","q4","q5",
  "q6","q7","q8","q9"
)

model_one <- '
  General =~
    q1 + q2 + q3 + q4 + q5 +
    q6 + q7 + q8 + q9
'

model_two <- '
  Factor1 =~
    q1 + q2 + q3 + q4 + q5

  Factor2 =~
    q6 + q7 + q8 + q9
'

model_reverse <- '
  General =~
    q1 + q2 + q3 + q4 + q5 +
    q6 + q7 + q8 + q9

  q4 ~~ q9
'

# Robust continuous-variable analysis with FIML.
fit_one_mlr <- cfa(
  model_one,
  data = data,
  estimator = "MLR",
  missing = "fiml",
  std.lv = TRUE
)

fit_two_mlr <- cfa(
  model_two,
  data = data,
  estimator = "MLR",
  missing = "fiml",
  std.lv = TRUE
)

fit_reverse_mlr <- cfa(
  model_reverse,
  data = data,
  estimator = "MLR",
  missing = "fiml",
  std.lv = TRUE
)

summary(
  fit_one_mlr,
  fit.measures = TRUE,
  standardized = TRUE,
  rsquare = TRUE
)

fitMeasures(
  fit_one_mlr,
  c(
    "chisq.scaled",
    "df.scaled",
    "pvalue.scaled",
    "cfi.robust",
    "tli.robust",
    "rmsea.robust",
    "srmr",
    "aic",
    "bic"
  )
)

anova(
  fit_one_mlr,
  fit_two_mlr
)

anova(
  fit_one_mlr,
  fit_reverse_mlr
)

standardizedSolution(
  fit_one_mlr
)

resid(
  fit_one_mlr,
  type = "cor"
)

modindices(
  fit_one_mlr,
  sort. = TRUE,
  minimum.value = 3.84
)

# Composite reliability from the fitted CFA model.
compRelSEM(
  fit_one_mlr
)

AVE(
  fit_one_mlr
)

# Ordinal sensitivity analysis.
fit_one_wlsmv <- cfa(
  model_one,
  data = data,
  ordered = items,
  estimator = "WLSMV",
  parameterization = "theta",
  std.lv = TRUE
)

summary(
  fit_one_wlsmv,
  fit.measures = TRUE,
  standardized = TRUE,
  rsquare = TRUE
)

# Save factor scores if needed.
factor_scores <- lavPredict(
  fit_one_mlr,
  method = "regression"
)

write.csv(
  factor_scores,
  "support/chapter17_lavaan_factor_scores.csv",
  row.names = FALSE
)