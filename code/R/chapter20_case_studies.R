# Chapter 20: reproducible case studies.
# Required packages:
# dplyr, readr, emmeans, sandwich, lmtest, lme4, lmerTest, pROC

library(dplyr)
library(readr)
library(emmeans)
library(sandwich)
library(lmtest)
library(lme4)
library(lmerTest)
library(pROC)

set.seed(20260720)

wide <- read_csv(
  "data/chapter20_master_wide.csv",
  show_col_types = FALSE
)

long <- read_csv(
  "data/chapter20_longitudinal_long.csv",
  show_col_types = FALSE
)

wide <- wide |>
  mutate(
    intervention = factor(
      intervention,
      levels = c("Control", "Workshop", "Blended")
    ),
    programme = factor(
      programme,
      levels = c("Masters", "Doctoral")
    )
  )

# Case Study 1
ancova_data <- wide |>
  filter(!is.na(Post), !is.na(Baseline)) |>
  mutate(
    baseline_c = Baseline - mean(Baseline),
    prior_c = prior_score - mean(prior_score)
  )

ancova_model <- lm(
  Post ~ baseline_c + intervention,
  data = ancova_data
)

summary(ancova_model)
coeftest(
  ancova_model,
  vcov. = vcovHC(ancova_model, type = "HC3")
)
emmeans(
  ancova_model,
  ~ intervention,
  at = list(baseline_c = 0)
)

homogeneity_model <- lm(
  Post ~ baseline_c * intervention + prior_c,
  data = ancova_data
)
anova(ancova_model, homogeneity_model)

# Case Study 2
mixed_data <- long |>
  filter(!is.na(research_score)) |>
  mutate(
    intervention = factor(
      intervention,
      levels = c("Control", "Workshop", "Blended")
    ),
    prior_c = prior_score - mean(prior_score)
  )

mixed_model <- lmer(
  research_score ~
    time + I(time^2) +
    intervention +
    time:intervention +
    prior_c +
    (1 + time | participant_id),
  data = mixed_data,
  REML = TRUE
)

summary(mixed_model)
VarCorr(mixed_model)

# Case Study 3
development <- wide |>
  filter(site %in% c("Site_A", "Site_B"))

validation <- wide |>
  filter(site == "Site_C")

logistic_model <- glm(
  completed_on_time ~
    I((prior_score - 72) / 10) +
    I((attendance_rate - 75) / 10) +
    I(self_efficacy_post - 3) +
    intervention +
    programme,
  family = binomial(),
  data = development
)

summary(logistic_model)
exp(cbind(OR = coef(logistic_model), confint(logistic_model)))

validation_probability <- predict(
  logistic_model,
  newdata = validation,
  type = "response"
)

validation_roc <- roc(
  validation$completed_on_time,
  validation_probability
)

auc(validation_roc)

mean(
  (
    validation$completed_on_time -
    validation_probability
  )^2
)

sessionInfo()