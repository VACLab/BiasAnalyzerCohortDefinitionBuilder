"""
Example 3: Cohort: Patients who had an inpatient visit (9201) within 90 days AFTER
a diabetes diagnosis (201826). No demographics constraints.
"""

from CohortDefinition import (
    ConditionOccurrence,
    VisitOccurrence,
    CohortCriteria,
    BEFORE,
)

# 1. Define the demographic filters
dm = ConditionOccurrence(event_concept_id=201826)   # Diabetes Mellitus
ip = VisitOccurrence(event_concept_id=9201)         # Inpatient visit

# 2. Define the event
visit_after_dm = BEFORE(ip, dm, offset=90)

# 3. Build the cohort YAML object
cohort = CohortCriteria(
    temporal_blocks=[visit_after_dm]
)

# 4. Dump YAML file
cohort.save("examples/example3.yaml")