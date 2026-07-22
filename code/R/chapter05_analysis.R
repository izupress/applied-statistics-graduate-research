# Chapter 5: statistical inference, effect sizes, and uncertainty.
# Run from the project root.
#
# Required packages:
# install.packages(c("dplyr", "ggplot2", "effectsize", "sandwich",
#                    "lmtest", "boot"))

library(dplyr)
library(ggplot2)
library(effectsize)
library(sandwich)
library(lmtest)
library(boot)

dat <- read.csv(
  "data/chapter05_randomised_study.csv",
  stringsAsFactors = FALSE
)

dat$group <- factor(
  dat$group,
  levels = c("Control", "Academic support")
)

group_summary <- dat |>
  group_by(group) |>
  summarise(
    n = n(),
    mean = mean(final_score),
    sd = sd(final_score),
    se = sd / sqrt(n),
    .groups = "drop"
  )

print(group_summary)

welch_test <- t.test(
  final_score ~ group,
  data = dat,
  var.equal = FALSE,
  conf.level = 0.95
)
print(welch_test)

# Standardised effect sizes.
print(
  cohens_d(
    final_score ~ group,
    data = dat,
    pooled_sd = TRUE,
    ci = 0.95
  )
)

print(
  hedges_g(
    final_score ~ group,
    data = dat,
    pooled_sd = TRUE,
    ci = 0.95
  )
)

# Baseline-adjusted treatment effect with HC3 standard errors.
adjusted_model <- lm(
  final_score ~ group + baseline_score,
  data = dat
)

print(
  coeftest(
    adjusted_model,
    vcov = vcovHC(
      adjusted_model,
      type = "HC3"
    )
  )
)

# Binary completion measures.
completion_table <- table(
  dat$group,
  dat$completion_status
)
print(completion_table)

risk_control <- completion_table[
  "Control",
  "Completed"
] / sum(completion_table["Control", ])

risk_support <- completion_table[
  "Academic support",
  "Completed"
] / sum(completion_table["Academic support", ])

risk_difference <- risk_support - risk_control
risk_ratio <- risk_support / risk_control

odds_support <- completion_table[
  "Academic support",
  "Completed"
] / completion_table[
  "Academic support",
  "Did not complete"
]

odds_control <- completion_table[
  "Control",
  "Completed"
] / completion_table[
  "Control",
  "Did not complete"
]

odds_ratio <- odds_support / odds_control

print(c(
  risk_control = risk_control,
  risk_support = risk_support,
  risk_difference = risk_difference,
  risk_ratio = risk_ratio,
  odds_ratio = odds_ratio
))

# Bootstrap percentile interval for the mean difference.
mean_difference_statistic <- function(data, indices) {
  sampled <- data[indices, ]
  means <- tapply(
    sampled$final_score,
    sampled$group,
    mean
  )
  means["Academic support"] - means["Control"]
}

set.seed(20260715)

bootstrap_result <- boot(
  data = dat,
  statistic = mean_difference_statistic,
  R = 5000,
  strata = dat$group
)

print(
  boot.ci(
    bootstrap_result,
    type = c("perc", "bca")
  )
)

# Randomisation/permutation test.
observed_difference <- with(
  dat,
  mean(final_score[group == "Academic support"]) -
  mean(final_score[group == "Control"])
)

permutation_reps <- 10000
permutation_differences <- numeric(permutation_reps)

for (i in seq_len(permutation_reps)) {
  permuted_group <- sample(dat$group)

  permutation_differences[i] <-
    mean(dat$final_score[
      permuted_group == "Academic support"
    ]) -
    mean(dat$final_score[
      permuted_group == "Control"
    ])
}

permutation_p <- (
  sum(
    abs(permutation_differences)
    >= abs(observed_difference)
  ) + 1
) / (permutation_reps + 1)

print(permutation_p)

ggplot(
  data.frame(value = bootstrap_result$t),
  aes(x = value)
) +
  geom_histogram(bins = 35) +
  geom_vline(xintercept = observed_difference) +
  labs(
    x = "Bootstrap mean difference",
    y = "Frequency",
    title = "Bootstrap distribution"
  )