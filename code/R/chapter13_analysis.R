# Chapter 13: mediation, moderation, and conditional process.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "ggplot2", "boot",
#   "sandwich", "lmtest"
# ))

library(dplyr)
library(ggplot2)
library(boot)
library(sandwich)
library(lmtest)

# ============================================================
# Simple and parallel mediation
# ============================================================
mediation <- read.csv(
  "data/chapter13_mediation.csv"
)

a_model <- lm(
  self_efficacy ~
    intervention +
    baseline_score,
  data = mediation
)

b_direct_model <- lm(
  final_score ~
    intervention +
    self_efficacy +
    baseline_score,
  data = mediation
)

total_model <- lm(
  final_score ~
    intervention +
    baseline_score,
  data = mediation
)

a_path <- coef(a_model)[
  "intervention"
]

b_path <- coef(b_direct_model)[
  "self_efficacy"
]

indirect_effect <- (
  a_path * b_path
)

print(
  c(
    a = a_path,
    b = b_path,
    indirect = indirect_effect,
    direct = coef(b_direct_model)[
      "intervention"
    ],
    total = coef(total_model)[
      "intervention"
    ]
  )
)

simple_boot_function <- function(
  data,
  indices
) {
  sampled <- data[
    indices,
  ]

  a_fit <- lm(
    self_efficacy ~
      intervention +
      baseline_score,
    data = sampled
  )

  b_fit <- lm(
    final_score ~
      intervention +
      self_efficacy +
      baseline_score,
    data = sampled
  )

  coef(a_fit)[
    "intervention"
  ] *
    coef(b_fit)[
      "self_efficacy"
    ]
}

set.seed(20260716)

simple_boot <- boot(
  data = mediation,
  statistic = simple_boot_function,
  R = 5000
)

print(
  boot.ci(
    simple_boot,
    type = c(
      "perc",
      "bca"
    )
  )
)

parallel_boot_function <- function(
  data,
  indices
) {
  sampled <- data[
    indices,
  ]

  m1_fit <- lm(
    self_efficacy ~
      intervention +
      baseline_score,
    data = sampled
  )

  m2_fit <- lm(
    engagement ~
      intervention +
      baseline_score,
    data = sampled
  )

  y_fit <- lm(
    final_score ~
      intervention +
      self_efficacy +
      engagement +
      baseline_score,
    data = sampled
  )

  indirect_1 <- (
    coef(m1_fit)[
      "intervention"
    ] *
      coef(y_fit)[
        "self_efficacy"
      ]
  )

  indirect_2 <- (
    coef(m2_fit)[
      "intervention"
    ] *
      coef(y_fit)[
        "engagement"
      ]
  )

  c(
    self_efficacy = indirect_1,
    engagement = indirect_2,
    total = indirect_1 + indirect_2
  )
}

parallel_boot <- boot(
  data = mediation,
  statistic = parallel_boot_function,
  R = 5000
)

print(
  apply(
    parallel_boot$t,
    2,
    quantile,
    probs = c(
      0.025,
      0.975
    )
  )
)

# ============================================================
# Moderation and Johnson-Neyman
# ============================================================
moderation <- read.csv(
  "data/chapter13_moderation.csv"
)

moderation_model <- lm(
  final_score ~
    study_hours_c *
    workload_c +
    prior_score,
  data = moderation
)

print(
  coeftest(
    moderation_model,
    vcov = vcovHC(
      moderation_model,
      type = "HC3"
    )
  )
)

robust_covariance <- vcovHC(
  moderation_model,
  type = "HC3"
)

b_x <- coef(
  moderation_model
)[
  "study_hours_c"
]

b_int <- coef(
  moderation_model
)[
  "study_hours_c:workload_c"
]

v_x <- robust_covariance[
  "study_hours_c",
  "study_hours_c"
]

v_int <- robust_covariance[
  "study_hours_c:workload_c",
  "study_hours_c:workload_c"
]

cov_x_int <- robust_covariance[
  "study_hours_c",
  "study_hours_c:workload_c"
]

workload_sd <- sd(
  moderation$workload
)

simple_slope <- function(
  moderator_value
) {
  slope <- (
    b_x +
      b_int *
      moderator_value
  )

  se <- sqrt(
    v_x +
      2 *
      moderator_value *
      cov_x_int +
      moderator_value^2 *
      v_int
  )

  t_value <- slope / se

  data.frame(
    moderator_value = moderator_value,
    slope = slope,
    standard_error = se,
    t_value = t_value,
    p_value = 2 *
      pt(
        abs(t_value),
        df = df.residual(
          moderation_model
        ),
        lower.tail = FALSE
      )
  )
}

print(
  bind_rows(
    simple_slope(
      -workload_sd
    ),
    simple_slope(
      0
    ),
    simple_slope(
      workload_sd
    )
  )
)

critical <- qt(
  0.975,
  df = df.residual(
    moderation_model
  )
)

quadratic_a <- (
  b_int^2 -
    critical^2 *
    v_int
)

quadratic_b <- (
  2 *
  b_x *
  b_int -
    2 *
    critical^2 *
    cov_x_int
)

quadratic_c <- (
  b_x^2 -
    critical^2 *
    v_x
)

jn_roots <- polyroot(
  c(
    quadratic_c,
    quadratic_b,
    quadratic_a
  )
)

print(
  Re(jn_roots)
)

prediction_grid <- read.csv(
  "support/chapter13_moderation_prediction_grid.csv"
)

ggplot(
  prediction_grid,
  aes(
    x = study_hours_original,
    y = predicted_final_score,
    group = workload_level,
    linetype = workload_level
  )
) +
  geom_line() +
  labs(
    x = "Weekly study hours",
    y = "Predicted final score",
    linetype = "Workload",
    title = "Study hours by workload interaction"
  )

# ============================================================
# First-stage moderated mediation
# ============================================================
conditional <- read.csv(
  "data/chapter13_conditional_process.csv"
)

mediator_model <- lm(
  self_efficacy ~
    intervention *
    workload_c +
    baseline_score,
  data = conditional
)

outcome_model <- lm(
  final_score ~
    intervention +
    self_efficacy +
    workload_c +
    baseline_score,
  data = conditional
)

a1 <- coef(
  mediator_model
)[
  "intervention"
]

a3 <- coef(
  mediator_model
)[
  "intervention:workload_c"
]

b_path <- coef(
  outcome_model
)[
  "self_efficacy"
]

index <- a3 * b_path

print(
  c(
    a1 = a1,
    a3 = a3,
    b = b_path,
    index = index
  )
)

conditional_boot_function <- function(
  data,
  indices,
  moderator_values
) {
  sampled <- data[
    indices,
  ]

  mediator_fit <- lm(
    self_efficacy ~
      intervention *
      workload_c +
      baseline_score,
    data = sampled
  )

  outcome_fit <- lm(
    final_score ~
      intervention +
      self_efficacy +
      workload_c +
      baseline_score,
    data = sampled
  )

  a1_boot <- coef(
    mediator_fit
  )[
    "intervention"
  ]

  a3_boot <- coef(
    mediator_fit
  )[
    "intervention:workload_c"
  ]

  b_boot <- coef(
    outcome_fit
  )[
    "self_efficacy"
  ]

  conditional_effects <- (
    a1_boot +
      a3_boot *
      moderator_values
  ) *
    b_boot

  c(
    index = a3_boot *
      b_boot,
    conditional_effects
  )
}

moderator_values <- c(
  -sd(
    conditional$workload
  ),
  0,
  sd(
    conditional$workload
  )
)

set.seed(20260718)

conditional_boot <- boot(
  data = conditional,
  statistic = function(
    data,
    indices
  ) {
    conditional_boot_function(
      data,
      indices,
      moderator_values
    )
  },
  R = 5000
)

print(
  apply(
    conditional_boot$t,
    2,
    quantile,
    probs = c(
      0.025,
      0.975
    )
  )
)