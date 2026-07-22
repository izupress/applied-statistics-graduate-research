# Chapter 10: correlation and simple regression.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "sandwich",
#   "lmtest", "boot", "mblm"
# ))

library(dplyr)
library(ggplot2)
library(sandwich)
library(lmtest)
library(boot)
library(mblm)

dat <- read.csv(
  "data/chapter10_correlation_regression.csv",
  stringsAsFactors = FALSE
)

# ------------------------------------------------------------
# Correlation
# ------------------------------------------------------------
pearson <- cor.test(
  dat$study_hours,
  dat$final_score,
  method = "pearson",
  conf.level = 0.95
)
print(pearson)

spearman <- cor.test(
  dat$study_hours,
  dat$final_score,
  method = "spearman",
  exact = FALSE
)
print(spearman)

kendall <- cor.test(
  dat$study_hours,
  dat$final_score,
  method = "kendall",
  exact = FALSE
)
print(kendall)

correlation_statistic <- function(data, indices) {
  sampled <- data[indices, ]
  cor(
    sampled$study_hours,
    sampled$final_score,
    method = "pearson"
  )
}

set.seed(20260716)

bootstrap_r <- boot(
  data = dat,
  statistic = correlation_statistic,
  R = 10000
)

print(
  boot.ci(
    bootstrap_r,
    type = c("perc", "bca")
  )
)

# ------------------------------------------------------------
# Simple regression
# ------------------------------------------------------------
model <- lm(
  final_score ~ study_hours,
  data = dat
)
summary(model)
confint(model)

coeftest(
  model,
  vcov = vcovHC(
    model,
    type = "HC3"
  )
)

# Predictions.
new_data <- data.frame(
  study_hours = c(5, 10, 15)
)

mean_prediction <- predict(
  model,
  newdata = new_data,
  interval = "confidence",
  level = 0.95
)

individual_prediction <- predict(
  model,
  newdata = new_data,
  interval = "prediction",
  level = 0.95
)

print(
  cbind(
    new_data,
    mean_prediction,
    individual_prediction[
      ,
      c("lwr", "upr")
    ]
  )
)

# Theil-Sen regression.
theil_sen <- mblm(
  final_score ~ study_hours,
  data = dat,
  repeated = FALSE
)
summary(theil_sen)

# Influence diagnostics.
diagnostics <- data.frame(
  student_id = dat$student_id,
  fitted = fitted(model),
  residual = residuals(model),
  studentized_residual = rstudent(model),
  leverage = hatvalues(model),
  cooks_distance = cooks.distance(model)
)

print(
  diagnostics |>
    arrange(desc(cooks_distance)) |>
    head(10)
)

bptest(model)

ggplot(
  dat,
  aes(
    x = study_hours,
    y = final_score
  )
) +
  geom_point(alpha = 0.65) +
  geom_smooth(
    method = "lm",
    se = TRUE
  ) +
  labs(
    x = "Weekly study hours",
    y = "Final score",
    title = "Study hours and final score"
  )

ggplot(
  data.frame(
    fitted = fitted(model),
    residual = residuals(model)
  ),
  aes(
    x = fitted,
    y = residual
  )
) +
  geom_point(alpha = 0.65) +
  geom_hline(yintercept = 0) +
  labs(
    x = "Fitted value",
    y = "Residual",
    title = "Residuals versus fitted values"
  )