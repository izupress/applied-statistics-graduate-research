# Chapter 19: measurement invariance with lavaan.

library(lavaan)

dat <- read.csv("data/chapter19_invariance_data.csv")
dat$programme <- relevel(factor(dat$programme), ref = "Masters")

model <- "factor =~ q1 + q2 + q3 + q4 + q5 + q6 + q7 + q8 + q9"

configural <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML"
)
metric <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = "loadings"
)
scalar <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = c("loadings", "intercepts")
)
partial_scalar <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = c("loadings", "intercepts"),
  group.partial = c("q4~1", "q9~1")
)
partial_strict <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = c("loadings", "intercepts", "residuals"),
  group.partial = c("q4~1", "q9~1")
)
equal_variance <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = c("loadings", "intercepts", "residuals", "lv.variances"),
  group.partial = c("q4~1", "q9~1")
)
equal_mean <- cfa(
  model, data = dat, group = "programme",
  meanstructure = TRUE, estimator = "ML",
  group.equal = c(
    "loadings", "intercepts", "residuals",
    "lv.variances", "means"
  ),
  group.partial = c("q4~1", "q9~1")
)

fits <- list(
  Configural = configural,
  Metric = metric,
  Scalar = scalar,
  Partial_scalar = partial_scalar,
  Partial_strict = partial_strict,
  Equal_variance = equal_variance,
  Equal_mean = equal_mean
)

fit_table <- do.call(rbind, lapply(fits, function(fit) {
  fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr"))
}))
print(round(fit_table, 4))

print(lavTestLRT(configural, metric))
print(lavTestLRT(metric, scalar))
print(lavTestLRT(metric, partial_scalar))
print(lavTestLRT(partial_scalar, partial_strict))
print(lavTestLRT(partial_strict, equal_variance))
print(lavTestLRT(equal_variance, equal_mean))

print(parameterEstimates(partial_scalar, standardized = TRUE))

# Robust sensitivity analysis.
partial_scalar_mlr <- update(partial_scalar, estimator = "MLR")
print(summary(partial_scalar_mlr, fit.measures = TRUE, standardized = TRUE))

# Optional ordinal sensitivity analysis after converting items to ordered
# categories. Threshold invariance replaces intercept invariance here.
ordered_dat <- dat
ordered_dat[paste0("q", 1:9)] <- lapply(
  ordered_dat[paste0("q", 1:9)],
  function(x) ordered(cut(x, breaks = quantile(x, 0:5 / 5), include.lowest = TRUE))
)
ordinal_metric <- cfa(
  model, data = ordered_dat, group = "programme",
  ordered = paste0("q", 1:9), estimator = "WLSMV",
  group.equal = "loadings"
)
ordinal_scalar <- cfa(
  model, data = ordered_dat, group = "programme",
  ordered = paste0("q", 1:9), estimator = "WLSMV",
  group.equal = c("loadings", "thresholds")
)
print(lavTestLRT(ordinal_metric, ordinal_scalar))