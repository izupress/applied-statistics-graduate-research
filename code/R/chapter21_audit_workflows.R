# Chapter 21 audit workflows.
# Required packages: readr, dplyr

library(readr)
library(dplyr)

reporting <- read_csv(
  "data/chapter21_reporting_audit.csv",
  show_col_types = FALSE
)

assets <- read_csv(
  "data/chapter21_open_science_assets.csv",
  show_col_types = FALSE
)

ai_log <- read_csv(
  "data/chapter21_ai_use_log.csv",
  show_col_types = FALSE
)

reporting |>
  group_by(
    study_design
  ) |>
  summarise(
    projects = n(),
    reporting = mean(
      reporting_score_percent
    ),
    open_science = mean(
      open_science_score_percent
    ),
    ethics = mean(
      ethics_transparency_score_percent
    ),
    overall = mean(
      overall_score_percent
    )
  )

reporting |>
  filter(
    critical_omission_count >
      0
  ) |>
  arrange(
    desc(
      critical_omission_count
    )
  ) |>
  select(
    project_id,
    study_design,
    critical_omission_count,
    audit_status
  )

assets |>
  group_by(
    recommended_access_plan
  ) |>
  summarise(
    assets = n(),
    fair_readiness = mean(
      fair_readiness_percent
    ),
    aligned_plans = sum(
      access_plan_aligned
    )
  )

ai_log |>
  group_by(
    risk_level
  ) |>
  summarise(
    uses = n(),
    compliant_uses = sum(
      compliant_use
    ),
    disclosure_gaps = sum(
      disclosure_gap
    ),
    confidentiality_violations = sum(
      confidentiality_violation
    )
  )

ai_log |>
  filter(
    risk_level != "Low"
  ) |>
  select(
    use_id,
    project_id,
    research_stage,
    task,
    risk_level,
    prohibited_flag
  )