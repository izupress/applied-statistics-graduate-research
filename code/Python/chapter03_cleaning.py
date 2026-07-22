"""Chapter 3 reproducible data-preparation pipeline.

Run from the project root:
    python code/Python/chapter03_cleaning.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/chapter03_raw_student_data.csv")
CLEAN = Path("data/chapter03_clean_student_data_python.csv")
AUDIT = Path("support/chapter03_audit_python.csv")

def canonical_key(value):
    if pd.isna(value):
        return pd.NA
    return (
        str(value).strip().upper()
        .replace("-", " ")
        .replace("_", " ")
    )

dat = pd.read_csv(RAW, dtype="string", keep_default_na=False)
raw_rows = len(dat)

for column in dat.columns:
    dat[column] = dat[column].str.strip()

dat["student_id"] = dat["student_id"].str.upper()
dat["record_version"] = pd.to_numeric(
    dat["record_version"], errors="coerce"
)

unique_ids = dat["student_id"].nunique(dropna=True)
extra_duplicate_rows = raw_rows - unique_ids

dat = (
    dat.sort_values(["student_id", "record_version"])
       .drop_duplicates("student_id", keep="last")
       .reset_index(drop=True)
)

date_text = dat["entry_date"].str.replace("/", "-", regex=False)
dat["entry_date_clean"] = pd.to_datetime(
    date_text, errors="coerce"
).dt.date

for source, target, lower, upper in [
    ("age", "age_clean", 18, 75),
    ("study_hours", "study_hours_clean", 0, 112),
    ("exam_score", "exam_score_clean", 0, 100),
]:
    dat[target] = pd.to_numeric(dat[source], errors="coerce")
    dat.loc[~dat[target].between(lower, upper), target] = np.nan

gender_map = {
    "F": "Female", "FEMALE": "Female", "WOMAN": "Female",
    "M": "Male", "MALE": "Male", "MAN": "Male",
    "NB": "Nonbinary", "NON BINARY": "Nonbinary",
    "NONBINARY": "Nonbinary",
    "PNS": "Prefer not to say",
    "PREFER NOT TO SAY": "Prefer not to say",
}
format_map = {
    "F2F": "Face-to-face",
    "FACE TO FACE": "Face-to-face",
    "ONLINE": "Online", "REMOTE": "Online",
    "HYB": "Hybrid", "HYBRID": "Hybrid",
}
completion_map = {
    "Y": "Completed", "1": "Completed",
    "COMPLETED": "Completed", "COMPLETE": "Completed",
    "N": "Did not complete", "0": "Did not complete",
    "DID NOT COMPLETE": "Did not complete",
    "NOT COMPLETED": "Did not complete",
}
consent_map = {
    "Y": "Yes", "YES": "Yes", "1": "Yes",
    "N": "No", "NO": "No", "0": "No",
}

dat["gender_clean"] = dat["gender"].map(
    lambda x: gender_map.get(canonical_key(x), pd.NA)
)
dat["instructional_format_clean"] = dat[
    "instructional_format"
].map(lambda x: format_map.get(canonical_key(x), pd.NA))
dat["completion_status_clean"] = dat[
    "completion_status"
].map(lambda x: completion_map.get(canonical_key(x), pd.NA))
dat["consent_clean"] = dat["consent"].map(
    lambda x: consent_map.get(canonical_key(x), pd.NA)
)

for j in range(1, 6):
    source = f"item{j}"
    target = f"{source}_clean"
    dat[target] = pd.to_numeric(dat[source], errors="coerce")
    dat.loc[~dat[target].between(1, 5), target] = np.nan

dat["item3_reverse"] = 6 - dat["item3_clean"]
dat["item5_reverse"] = 6 - dat["item5_clean"]

scored_items = [
    "item1_clean", "item2_clean", "item3_reverse",
    "item4_clean", "item5_reverse",
]
dat["scale_items_observed"] = dat[scored_items].notna().sum(axis=1)
dat["self_efficacy_score"] = dat[scored_items].mean(axis=1)
dat.loc[
    dat["scale_items_observed"] < 4,
    "self_efficacy_score",
] = np.nan

dat["age_group"] = pd.cut(
    dat["age_clean"],
    bins=[17, 24, 34, 44, 75],
    labels=["18-24", "25-34", "35-44", "45-75"],
)

analysis = dat.loc[dat["consent_clean"] == "Yes"].copy()

output = analysis[[
    "student_id", "record_version", "entry_date_clean",
    "age_clean", "age_group", "gender_clean",
    "instructional_format_clean", "study_hours_clean",
    "item1_clean", "item2_clean", "item3_clean",
    "item3_reverse", "item4_clean", "item5_clean",
    "item5_reverse", "scale_items_observed",
    "self_efficacy_score", "exam_score_clean",
    "completion_status_clean", "consent_clean",
]].rename(columns={
    "entry_date_clean": "entry_date",
    "age_clean": "age",
    "gender_clean": "gender",
    "instructional_format_clean": "instructional_format",
    "study_hours_clean": "study_hours",
    "item1_clean": "item1",
    "item2_clean": "item2",
    "item3_clean": "item3",
    "item4_clean": "item4",
    "item5_clean": "item5",
    "exam_score_clean": "exam_score",
    "completion_status_clean": "completion_status",
    "consent_clean": "consent",
})

output.to_csv(CLEAN, index=False)

audit = pd.DataFrame({
    "audit_item": [
        "Raw rows imported",
        "Unique normalised student identifiers",
        "Extra rows caused by repeated identifiers",
        "Rows retained after keeping highest record version",
        "Rows excluded because consent was not Yes",
        "Rows in final analysis data",
    ],
    "count": [
        raw_rows,
        unique_ids,
        extra_duplicate_rows,
        len(dat),
        int((dat["consent_clean"] != "Yes").sum()),
        len(output),
    ],
})
audit.to_csv(AUDIT, index=False)
print(audit.to_string(index=False))