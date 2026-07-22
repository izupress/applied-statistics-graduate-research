"""Generate SPSS companion syntax from the published CSV schemas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(".")
OUTPUT = ROOT / "code" / "SPSS"


def import_block(filename, dataset, force_string=()):
    path = ROOT / "data" / filename
    frame = pd.read_csv(path)
    variables = []
    for column in frame.columns:
        if (
            column not in force_string
            and pd.api.types.is_numeric_dtype(frame[column])
        ):
            variables.append(f"    {column} F14.6")
        else:
            width = int(frame[column].astype(str).str.len().max()) + 2
            variables.append(f"    {column} A{max(8, min(width, 255))}")
    variable_specification = "\n".join(variables)
    return f"""GET DATA
  /TYPE=TXT
  /FILE='data/{filename}'
  /ENCODING='UTF8'
  /DELCASE=LINE
  /DELIMITERS=\",\"
  /QUALIFIER='\"'
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /IMPORTCASE=ALL
  /VARIABLES=\n{variable_specification}.
CACHE.
DATASET NAME {dataset}.
EXECUTE.
"""


HEADER = """* Kitabın tamamlayıcı SPSS söz dizimi.
* Dosyayı depo ana klasörü çalışma diziniyken çalıştırın.
PRESERVE.
SET DECIMAL DOT.

"""
FOOTER = "\nRESTORE.\n"


SPECS = {
    "chapter02_analysis.sps": (
        [("chapter02_student_data.csv", "ch02")],
        """FREQUENCIES VARIABLES=instructional_format completion_status employment_status.
DESCRIPTIVES VARIABLES=exam_score study_hours self_efficacy /STATISTICS=MEAN STDDEV MIN MAX.
EXAMINE VARIABLES=exam_score study_hours BY instructional_format
  /PLOT=BOXPLOT HISTOGRAM NPPLOT /STATISTICS=DESCRIPTIVES PERCENTILES.
CORRELATIONS /VARIABLES=exam_score study_hours self_efficacy /PRINT=TWOTAIL.
""",
    ),
    "chapter03_cleaning.sps": (
        [(
            "chapter03_raw_student_data.csv",
            "ch03",
            {
                "record_version", "age", "study_hours",
                "item1", "item2", "item3", "item4", "item5",
                "exam_score",
            },
        )],
        """COMPUTE student_id_clean=UPCASE(LTRIM(RTRIM(student_id))).
COMPUTE record_version_n=NUMBER(LTRIM(RTRIM(record_version)),F8.0).
COMPUTE entry_date_standard=REPLACE(LTRIM(RTRIM(entry_date)),'/','-').
COMPUTE entry_date_n=NUMBER(entry_date_standard,EDATE10).
FORMATS entry_date_n (EDATE10).
SORT CASES BY student_id_clean(A) record_version_n(D) entry_date_n(D).
MATCH FILES FILE=* /BY student_id_clean /FIRST=latest_record.
SELECT IF latest_record=1.
COMPUTE age_clean=NUMBER(LTRIM(RTRIM(age)),F8.2).
COMPUTE exam_score_clean=NUMBER(LTRIM(RTRIM(exam_score)),F8.2).
COMPUTE study_hours_clean=NUMBER(LTRIM(RTRIM(study_hours)),F8.2).
IF NOT RANGE(age_clean,16,80) age_clean=$SYSMIS.
IF NOT RANGE(exam_score_clean,0,100) exam_score_clean=$SYSMIS.
IF NOT RANGE(study_hours_clean,0,80) study_hours_clean=$SYSMIS.
DO REPEAT raw=item1 item2 item3 item4 item5
 /clean=item1_clean item2_clean item3_clean item4_clean item5_clean.
  COMPUTE clean=NUMBER(LTRIM(RTRIM(raw)),F8.0).
  IF NOT RANGE(clean,1,5) clean=$SYSMIS.
END REPEAT.
FREQUENCIES VARIABLES=age_clean exam_score_clean study_hours_clean consent.
SAVE OUTFILE='data/chapter03_clean_student_data_SPSS.sav' /COMPRESSED.
""",
    ),
    "chapter04_analysis.sps": (
        [("chapter04_incomplete_data.csv", "ch04")],
        """MULTIPLE IMPUTATION age prior_gpa study_hours self_efficacy exam_score
  /IMPUTE METHOD=FCS NIMPUTATIONS=20 MAXPCTMISSING=50
  /MISSINGSUMMARIES OVERALL VARIABLES PATTERNS
  /IMPUTATIONSUMMARIES MODELS DESCRIPTIVES
  /OUTFILE IMPUTATIONS='data/chapter04_imputed_SPSS.sav'.
REGRESSION /DEPENDENT exam_score
  /METHOD=ENTER study_hours prior_gpa self_efficacy age
  /STATISTICS=COEFF OUTS R ANOVA CI(95) COLLIN TOL
  /SAVE=COOK LEVER SRESID.
""",
    ),
    "chapter05_analysis.sps": (
        [("chapter05_randomised_study.csv", "ch05")],
        """T-TEST GROUPS=group('Control' 'Academic support')
  /VARIABLES=improvement final_score /CRITERIA=CI(.95).
UNIANOVA final_score BY group WITH baseline_score
  /METHOD=SSTYPE(3) /INTERCEPT=INCLUDE
  /PRINT=DESCRIPTIVE PARAMETER ETASQ HOMOGENEITY
  /EMMEANS=TABLES(group) WITH(baseline_score=MEAN) COMPARE ADJ(BONFERRONI).
CROSSTABS /TABLES=group BY completion_status
  /STATISTICS=CHISQ RISK /CELLS=COUNT ROW EXPECTED.
""",
    ),
    "chapter06_planning.sps": (
        [("chapter06_planning_scenarios.csv", "ch06")],
        """COMPUTE z_alpha=IDF.NORMAL(1-alpha/2,0,1).
COMPUTE z_power=IDF.NORMAL(target_power,0,1).
COMPUTE analysis_n_per_group=$SYSMIS.
COMPUTE analysis_n_total=$SYSMIS.
COMPUTE design_effect=1.
COMPUTE variance_factor=1.

IF (design='Two independent means') analysis_n_per_group=
  CEIL(2*(z_alpha+z_power)**2*standard_deviation**2/target_value**2).

IF (design='Two independent proportions') p_bar=(control_value+target_value)/2.
IF (design='Two independent proportions') analysis_n_per_group=CEIL(
  (z_alpha*SQRT(2*p_bar*(1-p_bar))
  +z_power*SQRT(control_value*(1-control_value)
  +target_value*(1-target_value)))**2
  /(target_value-control_value)**2).

IF (design='Precision for one mean') analysis_n_total=
  CEIL((z_alpha*standard_deviation/ci_half_width)**2).

IF (design='Equivalence of two means') effective_margin=
  equivalence_margin-ABS(target_value-control_value).
IF (design='Equivalence of two means') analysis_n_per_group=CEIL(
  2*(IDF.NORMAL(1-alpha,0,1)+z_power)**2
  *standard_deviation**2/effective_margin**2).

IF (design='Cluster-randomised means') analysis_n_per_group=
  CEIL(2*(z_alpha+z_power)**2*standard_deviation**2/target_value**2).
IF (design='Cluster-randomised means') design_effect=
  1+(cluster_size-1)*icc.
IF (design='Cluster-randomised means') analysis_n_per_group=
  CEIL(analysis_n_per_group*design_effect).

IF (design='ANCOVA-adjusted means') analysis_n_per_group=
  CEIL(2*(z_alpha+z_power)**2*standard_deviation**2/target_value**2).
IF (design='ANCOVA-adjusted means') variance_factor=
  1-baseline_correlation**2.
IF (design='ANCOVA-adjusted means') analysis_n_per_group=
  CEIL(analysis_n_per_group*variance_factor).

COMPUTE recruitment_n_per_group=CEIL(
  analysis_n_per_group/(1-attrition_rate)).
COMPUTE recruitment_n_total=CEIL(
  analysis_n_total/(1-attrition_rate)).
FORMATS analysis_n_per_group analysis_n_total recruitment_n_per_group
  recruitment_n_total design_effect variance_factor (F10.3).
LIST VARIABLES=scenario_id design analysis_n_per_group analysis_n_total
  recruitment_n_per_group recruitment_n_total design_effect variance_factor.
""",
    ),
    "chapter07_analysis.sps": (
        [
            ("chapter07_independent_groups.csv", "independent"),
            ("chapter07_paired_study.csv", "paired"),
        ],
        """DATASET ACTIVATE independent.
T-TEST GROUPS=group_code(0 1) /VARIABLES=writing_score /CRITERIA=CI(.95).
CROSSTABS /TABLES=group_code BY passed /STATISTICS=CHISQ RISK /CELLS=COUNT ROW.
DATASET ACTIVATE paired.
T-TEST PAIRS=after_score WITH before_score (PAIRED) /CRITERIA=CI(.95).
NPAR TESTS /WILCOXON=after_score WITH before_score (PAIRED).
CROSSTABS /TABLES=confident_before BY confident_after /STATISTICS=MCNEMAR.
""",
    ),
    "chapter08_analysis.sps": (
        [
            ("chapter08_oneway_anova.csv", "oneway"),
            ("chapter08_factorial_design.csv", "factorial"),
        ],
        """DATASET ACTIVATE oneway.
ONEWAY final_score BY teaching_method
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH
  /POSTHOC=TUKEY GH ALPHA(.05).
DATASET ACTIVATE factorial.
UNIANOVA final_score BY feedback delivery_format WITH baseline_score
  /METHOD=SSTYPE(3) /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY PARAMETER
  /EMMEANS=TABLES(feedback*delivery_format) COMPARE(feedback) ADJ(BONFERRONI)
  /DESIGN=baseline_score feedback delivery_format feedback*delivery_format.
""",
    ),
    "chapter09_analysis.sps": (
        [
            ("chapter09_robust_groups.csv", "groups"),
            ("chapter09_repeated_measures.csv", "repeated"),
        ],
        """DATASET ACTIVATE groups.
ONEWAY productivity_score BY support_group
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH /POSTHOC=GH ALPHA(.05).
NPTESTS /INDEPENDENT TEST(productivity_score) GROUP(support_group)
  KRUSKAL_WALLIS(COMPARE=PAIRWISE).
DATASET ACTIVATE repeated.
NPAR TESTS /FRIEDMAN=stress_baseline stress_post stress_followup.
NPAR TESTS /WILCOXON=stress_post WITH stress_baseline (PAIRED).
""",
    ),
    "chapter10_analysis.sps": (
        [("chapter10_correlation_regression.csv", "ch10")],
        """CORRELATIONS /VARIABLES=study_hours final_score prior_score online_engagement
  /PRINT=TWOTAIL NOSIG.
NONPAR CORR /VARIABLES=study_hours final_score /PRINT=SPEARMAN TWOTAIL.
REGRESSION /DEPENDENT final_score /METHOD=ENTER study_hours
  /STATISTICS=COEFF OUTS R ANOVA CI(95)
  /SAVE=PRED RESID SRESID COOK LEVER.
GRAPH /SCATTERPLOT(BIVAR)=study_hours WITH final_score.
""",
    ),
    "chapter11_analysis.sps": (
        [("chapter11_multiple_regression.csv", "ch11")],
        """COMPUTE format_hybrid=(instructional_format='Hybrid').
COMPUTE format_online=(instructional_format='Online').
COMPUTE employ_parttime=(employment_status='Part-time').
COMPUTE employ_fulltime=(employment_status='Full-time').
VARIABLE LABELS
  format_hybrid 'Hybrid versus face-to-face'
  format_online 'Online versus face-to-face'
  employ_parttime 'Part-time versus not employed'
  employ_fulltime 'Full-time versus not employed'.
VALUE LABELS format_hybrid format_online employ_parttime employ_fulltime
  0 'No' 1 'Yes'.
EXECUTE.

DESCRIPTIVES VARIABLES=final_score prior_score study_hours online_engagement
  attendance_rate academic_self_efficacy /STATISTICS=MEAN STDDEV MIN MAX.
CORRELATIONS /VARIABLES=final_score prior_score study_hours online_engagement
  attendance_rate academic_self_efficacy /PRINT=TWOTAIL.

REGRESSION
  /MISSING=LISTWISE
  /DEPENDENT final_score
  /METHOD=ENTER prior_score
  /METHOD=ENTER study_hours online_engagement attendance_rate
    academic_self_efficacy
  /METHOD=ENTER format_hybrid format_online employ_parttime employ_fulltime
  /STATISTICS=COEFF OUTS R ANOVA CHANGE COLLIN TOL CI(95)
  /RESIDUALS=DURBIN HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /SCATTERPLOT=(*ZPRED,*ZRESID)
  /CASEWISE=OUTLIERS(3)
  /SAVE=PRED RESID SRESID COOK LEVER DFBETA.
""",
    ),
    "chapter12_analysis.sps": (
        [
            ("chapter12_binary_logistic.csv", "binary"),
            ("chapter12_count_regression.csv", "counts"),
            ("chapter12_gamma_regression.csv", "gamma"),
        ],
        """DATASET ACTIVATE binary.
GENLIN completed BY instructional_format employment_status
  WITH prior_score study_hours self_efficacy
  /MODEL instructional_format employment_status prior_score study_hours self_efficacy
    DISTRIBUTION=BINOMIAL LINK=LOGIT
  /PRINT CPS DESCRIPTIVES MODELINFO FIT SUMMARY SOLUTION(EXPONENTIATED).
DATASET ACTIVATE counts.
COMPUTE ln_exposure=LN(exposure_months).
GENLIN support_requests BY delivery_format employment_status
  WITH stress_score exposure_months
  /MODEL delivery_format employment_status stress_score OFFSET=ln_exposure
    DISTRIBUTION=POISSON LINK=LOG
  /PRINT MODELINFO FIT SUMMARY SOLUTION(EXPONENTIATED).
DATASET ACTIVATE gamma.
GENLIN completion_days WITH task_complexity team_size digital_support prior_experience_years
  /MODEL task_complexity team_size digital_support prior_experience_years
    DISTRIBUTION=GAMMA LINK=LOG
  /PRINT MODELINFO FIT SUMMARY SOLUTION(EXPONENTIATED).
""",
    ),
    "chapter13_analysis.sps": (
        [
            ("chapter13_mediation.csv", "mediation"),
            ("chapter13_moderation.csv", "moderation"),
            ("chapter13_conditional_process.csv", "conditional"),
        ],
        """DATASET ACTIVATE mediation.
REGRESSION /DEPENDENT self_efficacy /METHOD=ENTER intervention baseline_score.
REGRESSION /DEPENDENT final_score
  /METHOD=ENTER intervention self_efficacy engagement baseline_score.
DATASET ACTIVATE moderation.
COMPUTE study_x_workload=study_hours_c*workload_c.
REGRESSION /DEPENDENT final_score
  /METHOD=ENTER prior_score study_hours_c workload_c study_x_workload
  /STATISTICS=COEFF OUTS R ANOVA CHANGE CI(95) COLLIN TOL.
DATASET ACTIVATE conditional.
COMPUTE intervention_x_workload=intervention*workload_c.
REGRESSION /DEPENDENT self_efficacy
  /METHOD=ENTER intervention workload_c intervention_x_workload baseline_score.
REGRESSION /DEPENDENT final_score
  /METHOD=ENTER intervention self_efficacy workload_c baseline_score.
""",
    ),
    "chapter14_analysis.sps": (
        [
            ("chapter14_ancova.csv", "ancova"),
            ("chapter14_longitudinal.csv", "longitudinal"),
        ],
        """DATASET ACTIVATE ancova.
UNIANOVA post_score BY group WITH baseline_score
  /METHOD=SSTYPE(3) /PRINT=DESCRIPTIVE PARAMETER ETASQ HOMOGENEITY
  /EMMEANS=TABLES(group) WITH(baseline_score=MEAN) COMPARE ADJ(BONFERRONI)
  /DESIGN=baseline_score group.
DATASET ACTIVATE longitudinal.
MIXED outcome_score BY treatment WITH time_num prior_score
  /FIXED=intercept treatment time_num treatment*time_num prior_score | SSTYPE(3)
  /RANDOM=intercept time_num | SUBJECT(student_id) COVTYPE(UN)
  /METHOD=REML /PRINT=SOLUTION TESTCOV.
""",
    ),
    "chapter15_analysis.sps": (
        [
            ("chapter15_scale_items_raw.csv", "scale"),
            ("chapter15_test_retest.csv", "retest"),
            ("chapter15_interrater.csv", "raters"),
            ("chapter15_content_validity.csv", "content"),
        ],
        """DATASET ACTIVATE scale.
COMPUTE q4=6-q4_R.
COMPUTE q9=6-q9_R.
RELIABILITY /VARIABLES=q1 q2 q3 q4 q5 q6 q7 q8 q9 q10 q11 q12
  /SCALE('Draft') ALL /MODEL=ALPHA /STATISTICS=DESCRIPTIVE SCALE CORR.
RELIABILITY /VARIABLES=q1 q2 q3 q4 q5 q6 q7 q8 q9
  /SCALE('Final') ALL /MODEL=ALPHA /STATISTICS=DESCRIPTIVE SCALE CORR.
DATASET ACTIVATE retest.
RELIABILITY /VARIABLES=score_time1 score_time2 /ICC=MODEL(MIXED) TYPE(ABSOLUTE).
DATASET ACTIVATE raters.
RELIABILITY /VARIABLES=rater_1 rater_2 rater_3 /ICC=MODEL(MIXED) TYPE(ABSOLUTE).
DATASET ACTIVATE content.
COMPUTE relevant_flag=(relevance_rating_1_to_4 GE 3).
COMPUTE essential_flag=(essential_1_yes_0_no EQ 1).
AGGREGATE OUTFILE=* MODE=ADDVARIABLES /BREAK=item
  /expert_n=N /relevant_n=SUM(relevant_flag)
  /essential_n=SUM(essential_flag).
COMPUTE i_cvi=relevant_n/expert_n.
COMPUTE cvr=(essential_n-expert_n/2)/(expert_n/2).
FORMATS i_cvi cvr (F8.3).
LIST VARIABLES=item expert_n relevant_n essential_n i_cvi cvr.
""",
    ),
    "chapter16_analysis.sps": (
        [("chapter16_efa_items.csv", "efa")],
        """SELECT IF sample_role='Development'.
FACTOR /VARIABLES=q1 TO q12 /MISSING=LISTWISE
  /ANALYSIS=q1 TO q12 /PRINT=INITIAL EXTRACTION KMO REPR
  /PLOT=EIGEN /CRITERIA=FACTORS(2) ITERATE(100)
  /EXTRACTION=PAF /ROTATION=OBLIMIN /METHOD=CORRELATION.
""",
    ),
    "chapter17_data_preparation.sps": (
        [("chapter17_cfa_validation.csv", "cfa")],
        """SELECT IF sample_role='Validation'.
DESCRIPTIVES VARIABLES=q1 TO q9 /STATISTICS=MEAN STDDEV MIN MAX SKEWNESS KURTOSIS.
RELIABILITY /VARIABLES=q1 TO q9 /SCALE('CFA items') ALL /MODEL=ALPHA.
CORRELATIONS /VARIABLES=q1 TO q9 /MISSING=LISTWISE.
SAVE OUTFILE='data/chapter17_cfa_validation.sav' /COMPRESSED.
""",
    ),
    "chapter19_data_preparation.sps": (
        [("chapter19_invariance_data.csv", "invariance")],
        """COMPUTE programme_n=$SYSMIS.
IF (programme='Masters') programme_n=1.
IF (programme='Doctoral') programme_n=2.
VARIABLE LABELS programme_n 'Programme group for AMOS'.
VALUE LABELS programme_n 1 'Masters' 2 'Doctoral'.
FORMATS programme_n (F1.0).
EXECUTE.

FREQUENCIES VARIABLES=programme programme_n.
DESCRIPTIVES VARIABLES=q1 TO q9
  /STATISTICS=MEAN STDDEV MIN MAX SKEWNESS KURTOSIS.
RELIABILITY /VARIABLES=q1 TO q9
  /SCALE('Measurement invariance items') ALL
  /MODEL=ALPHA /STATISTICS=DESCRIPTIVE SCALE CORR.
SORT CASES BY programme_n participant_id.
SAVE OUTFILE='data/chapter19_invariance_data.sav' /COMPRESSED.
""",
    ),
    "chapter21_audit_workflows.sps": (
        [
            ("chapter21_reporting_audit.csv", "reporting"),
            ("chapter21_open_science_assets.csv", "assets"),
            ("chapter21_ai_use_log.csv", "ai_log"),
        ],
        """DATASET ACTIVATE reporting.
FREQUENCIES VARIABLES=audit_status study_design recommended_reporting_guideline.
DESCRIPTIVES VARIABLES=reporting_score_percent open_science_score_percent
  ethics_transparency_score_percent overall_score_percent critical_omission_count.
DATASET ACTIVATE assets.
FREQUENCIES VARIABLES=asset_type actual_access_plan recommended_access_plan
  access_plan_aligned release_priority.
DESCRIPTIVES VARIABLES=fair_readiness_percent.
DATASET ACTIVATE ai_log.
FREQUENCIES VARIABLES=research_stage risk_level compliant_use prohibited_flag
  confidentiality_violation verification_failure disclosure_gap.
""",
    ),
}


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, (datasets, commands) in SPECS.items():
        blocks = [HEADER]
        for dataset in datasets:
            blocks.append(import_block(*dataset))
        blocks.append(commands)
        blocks.append(FOOTER)
        (OUTPUT / filename).write_text("\n".join(blocks), encoding="utf-8")


if __name__ == "__main__":
    main()