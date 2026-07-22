# Chapter 9: robust and nonparametric methods.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "WRS2", "coin",
#   "sandwich", "lmtest", "quantreg", "rstatix", "tidyr"
# ))

library(dplyr)
library(ggplot2)
library(WRS2)
library(coin)
library(sandwich)
library(lmtest)
library(quantreg)
library(rstatix)
library(tidyr)

groups <- read.csv(
  "data/chapter09_robust_groups.csv",
  stringsAsFactors = FALSE
)
repeated <- read.csv(
  "data/chapter09_repeated_measures.csv",
  stringsAsFactors = FALSE
)

groups$support_group <- factor(
  groups$support_group,
  levels = c(
    "Standard support",
    "Peer mentoring",
    "AI-assisted planning"
  )
)

groups |>
  group_by(support_group) |>
  summarise(
    n = n(),
    mean = mean(productivity_score),
    sd = sd(productivity_score),
    median = median(productivity_score),
    trimmed_mean_20 = mean(productivity_score, trim = 0.20),
    mad = mad(productivity_score),
    .groups = "drop"
  ) |>
  print()

two_group <- groups |>
  filter(
    support_group %in% c(
      "Standard support",
      "Peer mentoring"
    )
  ) |>
  droplevels()

t.test(
  productivity_score ~ support_group,
  data = two_group,
  var.equal = FALSE
)

yuen(
  productivity_score ~ support_group,
  data = two_group,
  tr = 0.20
)

wilcox.test(
  productivity_score ~ support_group,
  data = two_group,
  exact = FALSE,
  conf.int = TRUE
)

oneway.test(
  productivity_score ~ support_group,
  data = groups,
  var.equal = FALSE
)

kruskal.test(
  productivity_score ~ support_group,
  data = groups
)

t1way(
  productivity_score ~ support_group,
  data = groups,
  tr = 0.20
)

groups |>
  dunn_test(
    productivity_score ~ support_group,
    p.adjust.method = "holm"
  ) |>
  print()

ols_model <- lm(
  productivity_score ~ support_group + baseline_score,
  data = groups
)

coeftest(
  ols_model,
  vcov = vcovHC(ols_model, type = "HC3")
)

median_model <- rq(
  productivity_score ~ support_group + baseline_score,
  tau = 0.50,
  data = groups
)
upper_model <- rq(
  productivity_score ~ support_group + baseline_score,
  tau = 0.75,
  data = groups
)

summary(median_model, se = "nid")
summary(upper_model, se = "nid")

repeated_long <- repeated |>
  pivot_longer(
    cols = c(
      stress_baseline,
      stress_post,
      stress_followup
    ),
    names_to = "time",
    values_to = "stress"
  )

repeated_long |>
  friedman_test(
    stress ~ time | participant_id
  ) |>
  print()

repeated_long |>
  pairwise_wilcox_test(
    stress ~ time,
    paired = TRUE,
    p.adjust.method = "holm"
  ) |>
  print()