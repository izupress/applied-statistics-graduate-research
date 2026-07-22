# Chapter 16: exploratory factor analysis.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "psych", "GPArotation"
# ))

library(dplyr)
library(psych)
library(GPArotation)

data <- read.csv(
  "data/chapter16_efa_development.csv"
)

draft_items <- c(
  "q1","q2","q3","q4","q5","q6",
  "q7","q8","q9","q10","q11","q12"
)

final_items <- c(
  "q1","q2","q3","q4","q5",
  "q6","q7","q8","q9"
)

draft <- data |>
  select(
    all_of(
      draft_items
    )
  ) |>
  na.omit()

final <- data |>
  select(
    all_of(
      final_items
    )
  ) |>
  na.omit()

draft_cor <- cor(
  draft,
  use = "pairwise.complete.obs"
)

print(
  KMO(
    draft_cor
  )
)

print(
  cortest.bartlett(
    draft_cor,
    n = nrow(
      draft
    )
  )
)

fa.parallel(
  draft,
  fa = "fa",
  fm = "pa",
  cor = "cor",
  n.iter = 1000
)

print(
  VSS(
    draft,
    n = 6,
    rotate = "oblimin",
    fm = "pa"
  )
)

one_factor <- fa(
  draft,
  nfactors = 1,
  fm = "pa",
  rotate = "none",
  scores = "regression"
)

print(one_factor)

two_factor <- fa(
  draft,
  nfactors = 2,
  fm = "pa",
  rotate = "oblimin",
  scores = "regression"
)

print(
  fa.sort(
    two_factor
  )
)

# Polychoric sensitivity analysis for ordinal items.
poly <- polychoric(
  draft
)

poly_two <- fa(
  poly$rho,
  nfactors = 2,
  n.obs = nrow(draft),
  fm = "minres",
  rotate = "oblimin"
)

print(
  fa.sort(
    poly_two
  )
)

final_one <- fa(
  final,
  nfactors = 1,
  fm = "pa",
  rotate = "none",
  scores = "regression"
)

print(final_one)