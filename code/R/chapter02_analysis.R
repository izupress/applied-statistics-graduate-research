library(readr)
library(dplyr)
library(ggplot2)
library(tidyr)

dat <- read_csv("data/chapter02_student_data.csv", show_col_types = FALSE)

missing_table <- dat |>
  summarise(across(everything(), ~sum(is.na(.x)))) |>
  pivot_longer(everything(), names_to = "variable", values_to = "missing_n") |>
  mutate(missing_pct = 100 * missing_n / nrow(dat))
print(missing_table)

format_table <- dat |>
  count(instructional_format) |>
  mutate(percent = 100 * n / sum(n))
print(format_table)

completion_table <- dat |>
  count(instructional_format, completion_status) |>
  group_by(instructional_format) |>
  mutate(row_percent = 100 * n / sum(n)) |>
  ungroup()
print(completion_table)

summary_table <- dat |>
  group_by(instructional_format) |>
  summarise(
    n_exam = sum(!is.na(exam_score)),
    mean_exam = mean(exam_score, na.rm = TRUE),
    sd_exam = sd(exam_score, na.rm = TRUE),
    median_exam = median(exam_score, na.rm = TRUE),
    q1_exam = quantile(exam_score, 0.25, na.rm = TRUE),
    q3_exam = quantile(exam_score, 0.75, na.rm = TRUE),
    min_exam = min(exam_score, na.rm = TRUE),
    max_exam = max(exam_score, na.rm = TRUE),
    .groups = "drop"
  )
print(summary_table)

ggplot(dat, aes(x = exam_score)) +
  geom_histogram(bins = 12, boundary = 0) +
  labs(x = "Examination score", y = "Number of students",
       title = "Distribution of examination scores")

ggplot(dat, aes(x = instructional_format, y = exam_score)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.12, height = 0) +
  labs(x = "Instructional format", y = "Examination score",
       title = "Examination scores by instructional format")

ggplot(dat, aes(x = study_hours, y = exam_score)) +
  geom_point() +
  geom_smooth(method = "lm", se = TRUE) +
  labs(x = "Weekly study time (hours)", y = "Examination score",
       title = "Study time and examination performance")