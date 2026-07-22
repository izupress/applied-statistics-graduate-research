# Chapter 11: multiple regression and diagnostics.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "car",
#   "sandwich", "lmtest", "performance",
#   "rsample", "yardstick"
# ))

library(dplyr)
library(ggplot2)
library(car)
library(sandwich)
library(lmtest)
library(performance)
library(rsample)
library(yardstick)

dat <- read.csv(
  "data/chapter11_multiple_regression.csv",
  stringsAsFactors = FALSE
)

analysis <- dat |>
  filter(
    !is.na(online_engagement),
    !is.na(attendance_rate)
  )

analysis$instructional_format <- factor(
  analysis$instructional_format,
  levels = c(
    "Face-to-face",
    "Hybrid",
    "Online"
  )
)

analysis$employment_status <- factor(
  analysis$employment_status,
  levels = c(
    "Not employed",
    "Part-time",
    "Full-time"
  )
)

model_1 <- lm(
  final_score ~ prior_score,
  data = analysis
)

model_2 <- lm(
  final_score ~
    prior_score +
    study_hours +
    online_engagement +
    attendance_rate +
    academic_self_efficacy,
  data = analysis
)

model_3 <- lm(
  final_score ~
    prior_score +
    study_hours +
    online_engagement +
    attendance_rate +
    academic_self_efficacy +
    instructional_format +
    employment_status,
  data = analysis
)

model_4 <- lm(
  final_score ~
    prior_score +
    study_hours +
    I(study_hours^2) +
    online_engagement +
    attendance_rate +
    academic_self_efficacy +
    instructional_format +
    employment_status,
  data = analysis
)

summary(model_3)
confint(model_3)

# HC3 inference.
coeftest(
  model_3,
  vcov = vcovHC(
    model_3,
    type = "HC3"
  )
)

# Nested model tests.
anova(
  model_1,
  model_2,
  model_3,
  model_4
)

# Multicollinearity.
vif(model_3)
check_collinearity(model_3)

# Diagnostics.
bptest(model_3)
resettest(
  model_3,
  power = 2:3,
  type = "fitted"
)

diagnostics <- data.frame(
  student_id = analysis$student_id,
  fitted = fitted(model_3),
  residual = residuals(model_3),
  studentised_residual = rstudent(model_3),
  leverage = hatvalues(model_3),
  cooks_distance = cooks.distance(model_3)
)

print(
  diagnostics |>
    arrange(desc(cooks_distance)) |>
    head(10)
)

# Standardised coefficients for continuous variables.
standardised <- analysis |>
  mutate(
    across(
      c(
        final_score,
        prior_score,
        study_hours,
        online_engagement,
        attendance_rate,
        academic_self_efficacy
      ),
      ~ as.numeric(scale(.x))
    )
  )

standardised_model <- lm(
  final_score ~
    prior_score +
    study_hours +
    online_engagement +
    attendance_rate +
    academic_self_efficacy +
    instructional_format +
    employment_status,
  data = standardised
)

summary(standardised_model)

# Residual plot.
ggplot(
  data.frame(
    fitted = fitted(model_3),
    residual = residuals(model_3)
  ),
  aes(
    x = fitted,
    y = residual
  )
) +
  geom_point(alpha = 0.60) +
  geom_hline(yintercept = 0) +
  labs(
    x = "Fitted value",
    y = "Residual",
    title = "Residuals versus fitted values"
  )

# Residual-leverage plot.
ggplot(
  diagnostics,
  aes(
    x = leverage,
    y = studentised_residual,
    size = cooks_distance
  )
) +
  geom_point(alpha = 0.55) +
  geom_hline(yintercept = 0) +
  labs(
    x = "Leverage",
    y = "Studentised residual",
    size = "Cook's distance",
    title = "Influence diagnostics"
  )