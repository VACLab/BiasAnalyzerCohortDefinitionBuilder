"""
Example 1: Men over 18 but less than 65, who have a diabetes diagnosis, 
followed by hospitalization with a subsequent COVID diagnosis.
We'd like data for these patients starting with their last diagnosis of diabetes prior to hospitalization, 
through 180 days after discharge from the hospital.
----------------------------------------------------------------------------
"""
from python_to_YAML import ConditionOccurrence, VisitOccurrence, Demographics, CohortYAML,OR, BEFORE


# 1. Define the demographic filters
demo = Demographics(gender="male", min_birth_year=1961, max_birth_year=2007)

# 2. Define the event: Heart failure diagnosis (Last T2DM or last T1DM)
t2_last = ConditionOccurrence(event_concept_id=201826, event_instance=-1)
t1_last = ConditionOccurrence(event_concept_id=201254, event_instance=-1)
dm_or = OR(t2_last, t1_last).to_yaml()   # OR returns a block; convert to dict for BEFORE

ip = VisitOccurrence(event_concept_id=9201)
covid = ConditionOccurrence(event_concept_id=37311061)

# (last DM) BEFORE (inpatient [+180 days])
inner = BEFORE(dm_or, ip, b_offset=180)

# inner BEFORE covid
outer = BEFORE(inner, covid)

# Build cohort: just pass the outer condition; CohortYAML will wrap top-level AND
cohort = CohortYAML(
    demographics=demo,
    temporal_blocks=[outer]
)

cohort.dump_yaml("examples/example1.yaml")