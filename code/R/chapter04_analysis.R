# Chapter 4: missing data, influence diagnostics, and robustness.
# Run from the project root.
#
# Required packages:
# install.packages(c("mice", "dplyr", "ggplot2", "broom", "MASS"))

library(mice)
library(dplyr)
library(ggplot2)
library(broom)
library(MASS)

dat <- read.csv(
  "data/chapter04_incomplete_data.csv",
  stringsAsFactors = FALSE
)

analysis_vars <- c(
  "age",
  "prior_gpa",
  "study_hours",
  "self_efficacy",
  "exam_score"
)

missing_summary <- data.frame(
  variable = analysis_vars,
  observed_n = sapply(
    dat[analysis_vars],
    function(x) sum(!is.na(x))
  ),
  missing_n = sapply(
    dat[analysis_vars],
    function(x) sum(is.na(x))
  ),
  missing_pct = sapply(
    dat[analysis_vars],
    function(x) 100 * mean(is.na(x))
  )
)

print(missing_summary)
md.pattern(dat[analysis_vars])

dat$m_exam_score <- as.integer(is.na(dat$exam_score))

missingness_model <- glm(
  m_exam_score ~ age + employment_status +
    instructional_format,
  data = dat,
  family = binomial()
)
summary(missingness_model)

model_variables <- c(
  "exam_score",
  "study_hours",
  "prior_gpa",
  "self_efficacy",
  "age"
)

complete_cases <- dat |>
  select(all_of(model_variables)) |>
  na.omit()

cc_fit <- lm(
  exam_score ~ study_hours + prior_gpa +
    self_efficacy + age,
  data = complete_cases
)
summary(cc_fit)

set.seed(20260715)

imputation_data <- dat |>
  select(
    age,
    prior_gpa,
    study_hours,
    self_efficacy,
    exam_score,
    instructional_format,
    employment_status,
    completion_status
  ) |>
  mutate(
    instructional_format = factor(instructional_format),
    employment_status = factor(employment_status),
    completion_status = factor(completion_status)
  )

method <- make.method(imputation_data)
method[c(
  "prior_gpa",
  "study_hours",
  "self_efficacy",
  "exam_score"
)] <- "pmm"

predictor_matrix <- make.predictorMatrix(imputation_data)

imp <- mice(
  imputation_data,
  m = 20,
  method = method,
  predictorMatrix = predictor_matrix,
  maxit = 20,
  seed = 20260715,
  printFlag = FALSE
)

plot(imp)
densityplot(imp, ~ exam_score)
stripplot(imp, exam_score ~ .imp, pch = 20)

mi_fit <- with(
  imp,
  lm(
    exam_score ~ study_hours + prior_gpa +
      self_efficacy + age
  )
)

pooled <- pool(mi_fit)
print(summary(pooled, conf.int = TRUE))

# Delta sensitivity analysis:
# Assume that missing exam scores are three points lower
# than their MAR imputations.
completed_sets <- complete(imp, action = "all")
missing_exam <- is.na(imputation_data$exam_score)

delta_fits <- lapply(
  completed_sets,
  function(data_i) {
    data_i$exam_score[missing_exam] <-
      data_i$exam_score[missing_exam] - 3

    lm(
      exam_score ~ study_hours + prior_gpa +
        self_efficacy + age,
      data = data_i
    )
  }
)

# mice::pool can pool a mira object; as.mira converts the list.
delta_pooled <- pool(as.mira(delta_fits))
print(summary(delta_pooled, conf.int = TRUE))

# Influence diagnostics on the first imputed data set.
first_complete <- complete(imp, 1)

ols_fit <- lm(
  exam_score ~ study_hours + prior_gpa +
    self_efficacy + age,
  data = first_complete
)

diagnostics <- data.frame(
  student_id = dat$student_id,
  studentized_residual = rstudent(ols_fit),
  leverage = hatvalues(ols_fit),
  cooks_distance = cooks.distance(ols_fit),
  dffits = dffits(ols_fit)
) |>
  arrange(desc(cooks_distance))

print(head(diagnostics, 10))

robust_fit <- rlm(
  exam_score ~ study_hours + prior_gpa +
    self_efficacy + age,
  data = first_complete,
  psi = psi.huber
)

summary(robust_fit)

ggplot(
  data.frame(
    fitted = fitted(ols_fit),
    studentized = rstudent(ols_fit)
  ),
  aes(x = fitted, y = studentized)
) +
  geom_point() +
  geom_hline(yintercept = 0) +
  labs(
    x = "Fitted examination score",
    y = "Externally studentized residual",
    title = "Residual diagnostic plot"
  )