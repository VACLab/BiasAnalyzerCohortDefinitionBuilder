"""
Example 1: Men over 18 but less than 65, who have a diabetes diagnosis,
followed by hospitalization with a subsequent COVID diagnosis.
We'd like data for these patients starting with their last diagnosis of diabetes prior to hospitalization,
through 180 days after discharge from the hospital.
"""
from CohortDefinition import (
    ConditionOccurrence,
    VisitOccurrence,
    Demographics,
    CohortCriteria,   # renamed
    OR,
    BEFORE,
)

# 1. Demographics
demo = Demographics(gender="male", min_birth_year=1961, max_birth_year=2007)

# 2. Events & logic
t2_last = ConditionOccurrence(event_concept_id=201826, event_instance=-1)  # last T2DM
t1_last = ConditionOccurrence(event_concept_id=201254, event_instance=-1)  # last T1DM
dm_or = OR(t2_last, t1_last)

ip = VisitOccurrence(event_concept_id=9201)               # Inpatient visit
covid = ConditionOccurrence(event_concept_id=37311061)    # COVID-19

inner = BEFORE(dm_or, ip, offset=180)  # (last DM) BEFORE (inpatient [+180d])
outer = BEFORE(inner, covid)           # inner BEFORE covid

# 3. Build criteria (no YAML handling from the user side)
cohort = CohortCriteria(
    demographics=demo,
    temporal_blocks=[outer],
)

# 4. Print to see YAML directly
print(cohort)

# 5. Save to disk when needed
cohort.save("examples/example1.yaml")