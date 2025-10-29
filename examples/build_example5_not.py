"""
Example 5: Test NOT operator alone
Goal: Build a cohort that includes patients who do NOT have heart failure diagnosis.
"""

from CohortDefinition import (
    ConditionOccurrence,
    CohortCriteria,
    NOT,
)


hf_dx = ConditionOccurrence(
    event_concept_id=316139  # Heart failure
)

not_hf = NOT(hf_dx)

cohort = CohortCriteria(
    temporal_blocks=[not_hf]
)

print(cohort.to_yaml())
cohort.save("examples/example5.yaml")
