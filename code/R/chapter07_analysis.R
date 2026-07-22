# Chapter 7: comparing two groups.
# Run from the project root.
#
# Required packages:
# install.packages(c("dplyr", "ggplot2", "effectsize", "coin"))

library(dplyr)
library(ggplot2)
library(effectsize)
library(coin)

independent <- read.csv(
  "data/chapter07_independent_groups.csv",
  stringsAsFactors = FALSE
)

paired <- read.csv(
  "data/chapter07_paired_study.csv",
  stringsAsFactors = FALSE
)

independent$group <- factor(
  independent$group,
  levels = c(
    "Standard instruction",
    "Structured feedback"
  )
)

# ------------------------------------------------------------
# Independent groups
# ------------------------------------------------------------
group_summary <- independent |>
  group_by(group) |>
  summarise(
    n = n(),
    mean = mean(writing_score),
    sd = sd(writing_score),
    median = median(writing_score),
    pass_risk = mean(passed),
    .groups = "drop"
  )

print(group_summary)

welch_result <- t.test(
  writing_score ~ group,
  data = independent,
  var.equal = FALSE,
  conf.level = 0.95
)
print(welch_result)

pooled_result <- t.test(
  writing_score ~ group,
  data = independent,
  var.equal = TRUE,
  conf.level = 0.95
)
print(pooled_result)

print(
  cohens_d(
    writing_score ~ group,
    data = independent,
    pooled_sd = TRUE,
    ci = 0.95
  )
)

print(
  hedges_g(
    writing_score ~ group,
    data = independent,
    pooled_sd = TRUE,
    ci = 0.95
  )
)

mann_whitney <- wilcox.test(
  writing_score ~ group,
  data = independent,
  exact = FALSE,
  conf.int = TRUE
)
print(mann_whitney)

# Randomisation/permutation test from the coin package.
permutation_result <- oneway_test(
  writing_score ~ group,
  data = independent,
  distribution = approximate(
    nresample = 10000
  )
)
print(permutation_result)

pass_table <- table(
  independent$group,
  independent$pass_status
)
print(pass_table)
print(prop.table(pass_table, margin = 1))

# ------------------------------------------------------------
# Paired data
# ------------------------------------------------------------
paired_t <- t.test(
  paired$after_score,
  paired$before_score,
  paired = TRUE,
  conf.level = 0.95
)
print(paired_t)

print(
  cohens_d(
    paired$after_score,
    paired$before_score,
    paired = TRUE,
    ci = 0.95
  )
)

paired$change_score <- (
  paired$after_score
  - paired$before_score
)

d_av <- mean(paired$change_score) /
  sqrt(
    (
      var(paired$before_score)
      + var(paired$after_score)
    ) / 2
  )

print(c(d_av = d_av))

wilcoxon_paired <- wilcox.test(
  paired$after_score,
  paired$before_score,
  paired = TRUE,
  exact = FALSE,
  conf.int = TRUE
)
print(wilcoxon_paired)

confidence_table <- table(
  paired$confident_before,
  paired$confident_after
)
print(confidence_table)
print(mcnemar.test(confidence_table, correct = FALSE))

ggplot(
  independent,
  aes(
    x = group,
    y = writing_score
  )
) +
  geom_boxplot() +
  geom_jitter(width = 0.08, alpha = 0.45) +
  labs(
    x = NULL,
    y = "Writing score",
    title = "Independent-group comparison"
  )

paired_long <- bind_rows(
  paired |>
    transmute(
      participant_id,
      time = "Before",
      score = before_score
    ),
  paired |>
    transmute(
      participant_id,
      time = "After",
      score = after_score
    )
)

ggplot(
  paired_long,
  aes(
    x = time,
    y = score,
    group = participant_id
  )
) +
  geom_line(alpha = 0.35) +
  geom_point(alpha = 0.45) +
  labs(
    x = NULL,
    y = "Research-methods score",
    title = "Paired before-after observations"
  )