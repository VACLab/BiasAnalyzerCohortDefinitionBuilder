"""
Heart failure cohort built with OHDSI id vs SNOMED code
"""

from CohortDefinition import (
    ConditionOccurrence,
    CohortCriteria,
)

# 1) Define the event using OHDSI concept_id
hf_ohdsi = ConditionOccurrence(
    event_concept_id=316139,   # Heart failure
    id_type="OHDSI",
)

# 2) Define the event using SNOMED
hf_snomed = ConditionOccurrence(
    event_concept_id=84114007, # Heart failure (SNOMED)
    id_type="SNOMED",
)

# 3) Build two cohorts
cohort_ohdsi = CohortCriteria(temporal_blocks=[hf_ohdsi])
cohort_snomed = CohortCriteria(temporal_blocks=[hf_snomed])

# 4) Print YAML (print emits YAML)
print("===== OHDSI version =====")
print(cohort_ohdsi)

print("===== SNOMED version =====")
print(cohort_snomed)
