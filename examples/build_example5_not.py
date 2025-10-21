"""
Example 5: Test NOT operator alone
Goal: Build a cohort that includes patients who do NOT have heart failure diagnosis.
"""

from python_to_YAML import (
    ConditionOccurrence,
    CohortYAML,
    NOT,
)


hf_dx = ConditionOccurrence(
    event_concept_id=316139  # Heart failure
)

not_hf = NOT(hf_dx)

cohort = CohortYAML(
    temporal_blocks=[not_hf]
)

cohort.save_yaml("examples/example5.yaml")
print(cohort)