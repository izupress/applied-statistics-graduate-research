# Chapter 12: generalized linear models.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "sandwich", "lmtest",
#   "MASS", "performance", "pROC", "marginaleffects",
#   "pscl"
# ))

library(dplyr)
library(ggplot2)
library(sandwich)
library(lmtest)
library(MASS)
library(performance)
library(pROC)
library(marginaleffects)
library(pscl)

# ============================================================
# Binary logistic regression
# ============================================================
binary <- read.csv(
  "data/chapter12_binary_logistic.csv",
  stringsAsFactors = FALSE
)

binary$instructional_format <- factor(
  binary$instructional_format,
  levels = c(
    "Face-to-face",
    "Hybrid",
    "Online"
  )
)

binary$employment_status <- factor(
  binary$employment_status,
  levels = c(
    "Not employed",
    "Part-time",
    "Full-time"
  )
)

logistic <- glm(
  completed ~
    prior_score +
    study_hours +
    self_efficacy +
    instructional_format +
    employment_status,
  data = binary,
  family = binomial(link = "logit")
)

summary(logistic)

odds_ratios <- data.frame(
  parameter = names(coef(logistic)),
  coefficient = coef(logistic),
  odds_ratio = exp(coef(logistic)),
  confint.default(logistic) |>
    exp()
)

print(odds_ratios)

# Average marginal effects.
avg_slopes(logistic)

# Modified Poisson with sandwich variance for risk ratios.
modified_poisson <- glm(
  completed ~
    prior_score +
    study_hours +
    self_efficacy +
    instructional_format +
    employment_status,
  data = binary,
  family = poisson(link = "log")
)

coeftest(
  modified_poisson,
  vcov = vcovHC(
    modified_poisson,
    type = "HC0"
  )
)

risk_ratios <- exp(
  coef(modified_poisson)
)
print(risk_ratios)

predicted_probability <- predict(
  logistic,
  type = "response"
)

roc_object <- roc(
  binary$completed,
  predicted_probability
)

print(auc(roc_object))

performance::check_model(logistic)

# ============================================================
# Count regression
# ============================================================
count <- read.csv(
  "data/chapter12_count_regression.csv",
  stringsAsFactors = FALSE
)

count$delivery_format <- factor(
  count$delivery_format,
  levels = c(
    "Face-to-face",
    "Hybrid",
    "Online"
  )
)

count$employment_status <- factor(
  count$employment_status,
  levels = c(
    "Not employed",
    "Part-time",
    "Full-time"
  )
)

poisson_model <- glm(
  support_requests ~
    stress_score +
    delivery_format +
    employment_status +
    offset(log(exposure_months)),
  data = count,
  family = poisson(link = "log")
)

summary(poisson_model)

poisson_dispersion <- sum(
  residuals(
    poisson_model,
    type = "pearson"
  )^2
) / df.residual(poisson_model)

print(poisson_dispersion)

negative_binomial <- glm.nb(
  support_requests ~
    stress_score +
    delivery_format +
    employment_status +
    offset(log(exposure_months)),
  data = count
)

summary(negative_binomial)

print(
  exp(
    cbind(
      Estimate = coef(negative_binomial),
      confint.default(
        negative_binomial
      )
    )
  )
)

# Optional zero-inflated Poisson sensitivity.
zero_inflated_poisson <- zeroinfl(
  support_requests ~
    stress_score +
    delivery_format +
    employment_status +
    offset(log(exposure_months))
  | 1,
  data = count,
  dist = "poisson"
)

summary(zero_inflated_poisson)

# ============================================================
# Gamma regression
# ============================================================
gamma_data <- read.csv(
  "data/chapter12_gamma_regression.csv",
  stringsAsFactors = FALSE
)

gamma_model <- glm(
  completion_days ~
    task_complexity +
    team_size +
    digital_support +
    prior_experience_years,
  data = gamma_data,
  family = Gamma(link = "log")
)

summary(gamma_model)

gamma_ratios <- exp(
  cbind(
    Estimate = coef(gamma_model),
    confint.default(gamma_model)
  )
)

print(gamma_ratios)

coeftest(
  gamma_model,
  vcov = vcovHC(
    gamma_model,
    type = "HC3"
  )
)

ggplot(
  data.frame(
    fitted = fitted(gamma_model),
    residual = residuals(
      gamma_model,
      type = "deviance"
    )
  ),
  aes(
    x = fitted,
    y = residual
  )
) +
  geom_point(alpha = 0.60) +
  geom_hline(yintercept = 0) +
  labs(
    x = "Predicted mean completion days",
    y = "Deviance residual",
    title = "Gamma-regression diagnostics"
  )