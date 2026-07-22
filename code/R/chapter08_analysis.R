# Chapter 8: ANOVA and factorial designs.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "car", "effectsize",
#   "emmeans", "rstatix"
# ))

library(dplyr)
library(ggplot2)
library(car)
library(effectsize)
library(emmeans)
library(rstatix)

oneway <- read.csv(
  "data/chapter08_oneway_anova.csv",
  stringsAsFactors = FALSE
)

factorial <- read.csv(
  "data/chapter08_factorial_design.csv",
  stringsAsFactors = FALSE
)

# ------------------------------------------------------------
# One-way ANOVA
# ------------------------------------------------------------
oneway$teaching_method <- factor(
  oneway$teaching_method
)

oneway |>
  group_by(teaching_method) |>
  summarise(
    n = n(),
    mean = mean(final_score),
    sd = sd(final_score),
    median = median(final_score),
    .groups = "drop"
  ) |>
  print()

classic_model <- aov(
  final_score ~ teaching_method,
  data = oneway
)
summary(classic_model)

oneway.test(
  final_score ~ teaching_method,
  data = oneway,
  var.equal = FALSE
)

leveneTest(
  final_score ~ teaching_method,
  data = oneway,
  center = median
)

eta_squared(
  classic_model,
  partial = FALSE
)

omega_squared(
  classic_model,
  partial = FALSE
)

TukeyHSD(classic_model)

oneway |>
  games_howell_test(
    final_score ~ teaching_method
  ) |>
  print()

# Planned contrasts.
contrasts(oneway$teaching_method) <- cbind(
  lecture_vs_active = c(
    -1,
    1 / 3,
    1 / 3,
    1 / 3
  ),
  adaptive_vs_other_active = c(
    0,
    -1 / 2,
    -1 / 2,
    1
  )
)

contrast_model <- lm(
  final_score ~ teaching_method,
  data = oneway
)
summary(contrast_model)

# ------------------------------------------------------------
# Two-factor design
# ------------------------------------------------------------
factorial$feedback <- factor(
  factorial$feedback,
  levels = c(
    "Standard feedback",
    "Structured feedback"
  )
)

factorial$delivery_format <- factor(
  factorial$delivery_format,
  levels = c(
    "Face-to-face",
    "Online",
    "Hybrid"
  )
)

contrasts(factorial$feedback) <- contr.sum(2)
contrasts(factorial$delivery_format) <- contr.sum(3)

factorial_model <- lm(
  final_score ~
    feedback * delivery_format,
  data = factorial
)

Anova(
  factorial_model,
  type = 3
)

eta_squared(
  factorial_model,
  partial = TRUE
)

omega_squared(
  factorial_model,
  partial = TRUE
)

emm_feedback <- emmeans(
  factorial_model,
  ~ feedback
)
print(emm_feedback)

emm_delivery <- emmeans(
  factorial_model,
  ~ delivery_format
)
print(emm_delivery)

emm_cells <- emmeans(
  factorial_model,
  ~ feedback * delivery_format
)
print(emm_cells)

# Simple feedback effects within each delivery format.
simple_feedback <- emmeans(
  factorial_model,
  pairwise ~ feedback |
    delivery_format,
  adjust = "holm"
)
print(simple_feedback)

# Simple delivery-format effects within each feedback condition.
simple_delivery <- emmeans(
  factorial_model,
  pairwise ~ delivery_format |
    feedback,
  adjust = "tukey"
)
print(simple_delivery)

factorial |>
  group_by(
    feedback,
    delivery_format
  ) |>
  summarise(
    n = n(),
    mean = mean(final_score),
    sd = sd(final_score),
    .groups = "drop"
  ) |>
  ggplot(
    aes(
      x = delivery_format,
      y = mean,
      group = feedback,
      linetype = feedback
    )
  ) +
  geom_line() +
  geom_point() +
  labs(
    x = "Delivery format",
    y = "Mean final score",
    linetype = "Feedback",
    title = "Feedback by delivery-format interaction"
  )