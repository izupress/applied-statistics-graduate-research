# Chapter 15: reliability, measurement error, and scale development.
# Run from the project root.
#
# Required packages:
# install.packages(c(
#   "dplyr", "psych", "irr"
# ))

library(dplyr)
library(psych)
library(irr)

raw <- read.csv(
  "data/chapter15_scale_items_raw.csv"
)

raw$q4 <- 6 - raw$q4_R
raw$q9 <- 6 - raw$q9_R

draft_items <- c(
  "q1","q2","q3","q4","q5","q6",
  "q7","q8","q9","q10","q11","q12"
)

final_items <- c(
  "q1","q2","q3","q4","q5",
  "q6","q7","q8","q9"
)

draft <- raw |>
  select(
    all_of(
      draft_items
    )
  ) |>
  na.omit()

final <- raw |>
  select(
    all_of(
      final_items
    )
  ) |>
  na.omit()

print(
  psych::alpha(
    draft,
    check.keys = FALSE
  )
)

print(
  psych::alpha(
    final,
    check.keys = FALSE
  )
)

print(
  psych::omega(
    final,
    nfactors = 1,
    plot = FALSE
  )
)

content <- read.csv(
  "data/chapter15_content_validity.csv"
)

content_results <- content |>
  group_by(item) |>
  summarise(
    experts = n_distinct(
      expert_id
    ),
    relevant_n = sum(
      relevance_rating_1_to_4 >= 3
    ),
    essential_n = sum(
      essential_1_yes_0_no
    ),
    i_cvi = relevant_n /
      experts,
    cvr = (
      essential_n -
        experts / 2
    ) / (
      experts / 2
    )
  )

print(content_results)

test_retest <- read.csv(
  "data/chapter15_test_retest.csv"
)

print(
  irr::icc(
    test_retest[
      c(
        "score_time1",
        "score_time2"
      )
    ],
    model = "twoway",
    type = "agreement",
    unit = "single",
    conf.level = 0.95
  )
)

interrater <- read.csv(
  "data/chapter15_interrater.csv"
)

print(
  irr::icc(
    interrater[
      c(
        "rater_1",
        "rater_2",
        "rater_3"
      )
    ],
    model = "twoway",
    type = "agreement",
    unit = "single",
    conf.level = 0.95
  )
)