# Chapter 3 reproducible data-preparation pipeline
# Run from the project root.

library(readr)
library(dplyr)
library(stringr)

dat <- read_csv(
  "data/chapter03_raw_student_data.csv",
  col_types = cols(.default = col_character()),
  na = character()
)
raw_rows <- nrow(dat)

dat <- dat |>
  mutate(
    across(everything(), str_trim),
    student_id = str_to_upper(student_id),
    record_version = suppressWarnings(as.numeric(record_version))
  )

unique_ids <- n_distinct(dat$student_id)
extra_duplicate_rows <- raw_rows - unique_ids

dat <- dat |>
  arrange(student_id, record_version) |>
  group_by(student_id) |>
  slice_tail(n = 1) |>
  ungroup()

normalise_key <- function(x) {
  x |>
    str_trim() |>
    str_to_upper() |>
    str_replace_all("[-_]", " ")
}

date_text <- str_replace_all(dat$entry_date, "/", "-")
dat$entry_date_clean <- suppressWarnings(as.Date(date_text))

dat$age_clean <- suppressWarnings(as.numeric(dat$age))
dat$age_clean[
  is.na(dat$age_clean) |
  dat$age_clean < 18 |
  dat$age_clean > 75
] <- NA_real_

dat$study_hours_clean <- suppressWarnings(as.numeric(dat$study_hours))
dat$study_hours_clean[
  is.na(dat$study_hours_clean) |
  dat$study_hours_clean < 0 |
  dat$study_hours_clean > 112
] <- NA_real_

dat$exam_score_clean <- suppressWarnings(as.numeric(dat$exam_score))
dat$exam_score_clean[
  is.na(dat$exam_score_clean) |
  dat$exam_score_clean < 0 |
  dat$exam_score_clean > 100
] <- NA_real_

gender_key <- normalise_key(dat$gender)
dat$gender_clean <- case_when(
  gender_key %in% c("F", "FEMALE", "WOMAN") ~ "Female",
  gender_key %in% c("M", "MALE", "MAN") ~ "Male",
  gender_key %in% c("NB", "NON BINARY", "NONBINARY") ~ "Nonbinary",
  gender_key %in% c("PNS", "PREFER NOT TO SAY") ~ "Prefer not to say",
  TRUE ~ NA_character_
)

format_key <- normalise_key(dat$instructional_format)
dat$instructional_format_clean <- case_when(
  format_key %in% c("F2F", "FACE TO FACE") ~ "Face-to-face",
  format_key %in% c("ONLINE", "REMOTE") ~ "Online",
  format_key %in% c("HYB", "HYBRID") ~ "Hybrid",
  TRUE ~ NA_character_
)

completion_key <- normalise_key(dat$completion_status)
dat$completion_status_clean <- case_when(
  completion_key %in% c("Y", "1", "COMPLETED", "COMPLETE") ~ "Completed",
  completion_key %in% c("N", "0", "DID NOT COMPLETE", "NOT COMPLETED") ~
    "Did not complete",
  TRUE ~ NA_character_
)

consent_key <- normalise_key(dat$consent)
dat$consent_clean <- case_when(
  consent_key %in% c("Y", "YES", "1") ~ "Yes",
  consent_key %in% c("N", "NO", "0") ~ "No",
  TRUE ~ NA_character_
)

for (j in 1:5) {
  source <- paste0("item", j)
  target <- paste0(source, "_clean")
  values <- suppressWarnings(as.numeric(dat[[source]]))
  values[is.na(values) | values < 1 | values > 5] <- NA_real_
  dat[[target]] <- values
}

dat <- dat |>
  mutate(
    item3_reverse = 6 - item3_clean,
    item5_reverse = 6 - item5_clean
  )

scored <- dat |>
  select(item1_clean, item2_clean, item3_reverse,
         item4_clean, item5_reverse)

dat$scale_items_observed <- rowSums(!is.na(scored))
dat$self_efficacy_score <- rowMeans(scored, na.rm = TRUE)
dat$self_efficacy_score[
  dat$scale_items_observed < 4
] <- NA_real_

dat$age_group <- cut(
  dat$age_clean,
  breaks = c(17, 24, 34, 44, 75),
  labels = c("18-24", "25-34", "35-44", "45-75")
)

analysis <- dat |>
  filter(consent_clean == "Yes") |>
  transmute(
    student_id,
    record_version,
    entry_date = entry_date_clean,
    age = age_clean,
    age_group,
    gender = gender_clean,
    instructional_format = instructional_format_clean,
    study_hours = study_hours_clean,
    item1 = item1_clean,
    item2 = item2_clean,
    item3 = item3_clean,
    item3_reverse,
    item4 = item4_clean,
    item5 = item5_clean,
    item5_reverse,
    scale_items_observed,
    self_efficacy_score,
    exam_score = exam_score_clean,
    completion_status = completion_status_clean,
    consent = consent_clean
  )

write_csv(
  analysis,
  "data/chapter03_clean_student_data_R.csv"
)

audit <- tibble(
  audit_item = c(
    "Raw rows imported",
    "Unique normalised student identifiers",
    "Extra rows caused by repeated identifiers",
    "Rows retained after keeping highest record version",
    "Rows excluded because consent was not Yes",
    "Rows in final analysis data"
  ),
  count = c(
    raw_rows,
    unique_ids,
    extra_duplicate_rows,
    nrow(dat),
    sum(dat$consent_clean != "Yes" | is.na(dat$consent_clean)),
    nrow(analysis)
  )
)

write_csv(audit, "support/chapter03_audit_R.csv")
print(audit)