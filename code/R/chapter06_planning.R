# Chapter 6: power, sensitivity, and sample-size planning.
# Run from the project root.
#
# Required packages:
# install.packages(c("dplyr", "ggplot2"))

library(dplyr)
library(ggplot2)

scenarios <- read.csv(
  "data/chapter06_planning_scenarios.csv",
  stringsAsFactors = FALSE
)

# Two independent means.
mean_plan <- power.t.test(
  delta = 5,
  sd = 12,
  sig.level = 0.05,
  power = 0.80,
  type = "two.sample",
  alternative = "two.sided"
)

analysis_n_per_group <- ceiling(mean_plan$n)
recruit_n_per_group <- ceiling(
  analysis_n_per_group / (1 - 0.15)
)

print(mean_plan)
print(c(
  analysis_n_per_group = analysis_n_per_group,
  recruit_n_per_group = recruit_n_per_group
))

# Two independent proportions.
proportion_plan <- power.prop.test(
  p1 = 0.60,
  p2 = 0.75,
  sig.level = 0.05,
  power = 0.80,
  alternative = "two.sided"
)

print(proportion_plan)

# Precision-based planning for one mean.
sigma <- 10
half_width <- 2
z_critical <- qnorm(0.975)

n_precision <- ceiling(
  (z_critical * sigma / half_width)^2
)

print(c(
  precision_analysis_n = n_precision,
  precision_recruit_n = ceiling(
    n_precision / 0.90
  )
))

# Cluster design effect.
cluster_size <- 20
icc <- 0.05

design_effect <- 1 + (cluster_size - 1) * icc

print(c(
  design_effect = design_effect,
  individual_equivalent_total = ceiling(
    2 * analysis_n_per_group * design_effect
  )
))

# Approximate ANCOVA efficiency.
baseline_correlation <- 0.60
variance_factor <- 1 - baseline_correlation^2

print(c(
  variance_factor = variance_factor,
  adjusted_n_per_group = ceiling(
    analysis_n_per_group * variance_factor
  )
))

# Power curve.
differences <- seq(1, 8, by = 0.5)
sample_sizes <- c(40, 60, 80, 100, 120, 160, 200)

power_curve <- expand.grid(
  difference = differences,
  n_per_group = sample_sizes
) |>
  rowwise() |>
  mutate(
    power = power.t.test(
      n = n_per_group,
      delta = difference,
      sd = 12,
      sig.level = 0.05,
      type = "two.sample",
      alternative = "two.sided"
    )$power
  ) |>
  ungroup()

ggplot(
  power_curve,
  aes(
    x = difference,
    y = power,
    group = factor(n_per_group),
    linetype = factor(n_per_group)
  )
) +
  geom_line() +
  geom_hline(yintercept = 0.80) +
  labs(
    x = "True mean difference",
    y = "Power",
    linetype = "n per group",
    title = "Power as a function of effect and sample size"
  )

# Type S and Type M simulation.
set.seed(20260715)

simulate_errors <- function(
  n_per_group,
  true_difference = 3,
  sigma = 12,
  repetitions = 20000
) {
  estimates <- numeric(repetitions)
  significant <- logical(repetitions)

  for (i in seq_len(repetitions)) {
    y1 <- rnorm(
      n_per_group,
      mean = true_difference,
      sd = sigma
    )
    y0 <- rnorm(
      n_per_group,
      mean = 0,
      sd = sigma
    )

    result <- t.test(
      y1,
      y0,
      var.equal = FALSE
    )

    estimates[i] <- mean(y1) - mean(y0)
    significant[i] <- result$p.value < 0.05
  }

  selected <- estimates[significant]

  data.frame(
    n_per_group = n_per_group,
    empirical_power = mean(significant),
    type_s = mean(selected < 0),
    type_m = mean(abs(selected)) /
      abs(true_difference),
    mean_estimate_all = mean(estimates),
    mean_estimate_significant = mean(selected)
  )
}

type_sm <- bind_rows(
  lapply(
    c(25, 50, 100, 200),
    simulate_errors
  )
)

print(type_sm)