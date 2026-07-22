library(dplyr)
library(sandwich)
library(lmtest)
library(afex)
library(lme4)
library(lmerTest)
library(emmeans)

anc <- read.csv("data/chapter14_ancova.csv")
anc$group <- factor(anc$group,
  levels=c("Control","Workshop","Blended"))
ancova <- lm(post_score ~ baseline_score + group, data=anc)
coeftest(ancova, vcov=vcovHC(ancova, type="HC3"))
anova(ancova, lm(post_score ~ baseline_score * group, data=anc))
emmeans(ancova, ~group, cov.reduce=mean)

long <- read.csv("data/chapter14_longitudinal.csv")
long$time <- factor(long$time,
  levels=c("Baseline","Post","Follow-up"))
long$treatment <- factor(long$treatment,
  levels=c("Control","Intervention"))

complete_ids <- long |>
  group_by(student_id) |>
  summarise(ok=all(!is.na(outcome_score))) |>
  filter(ok) |>
  pull(student_id)

balanced <- long |> filter(student_id %in% complete_ids)

rm <- aov_car(
  outcome_score ~ treatment*time + Error(student_id/time),
  data=balanced,
  factorize=FALSE
)
print(rm)

mixed <- lmer(
  outcome_score ~ time_num*treatment + I(time_num^2) + prior_score +
    (1+time_num|student_id),
  data=long,
  REML=TRUE,
  na.action=na.exclude
)
summary(mixed)
emmeans(mixed, ~treatment*time_num, at=list(time_num=c(0,1,2)))