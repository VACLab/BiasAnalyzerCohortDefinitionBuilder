"""
Example 2: Male patients born in or before 1990 diagnosed with heart failure
----------------------------------------------------------------------------
"""

from CohortDefinition import ConditionOccurrence, Demographics, CohortCriteria

# 1. Define the demographic filters
demo = Demographics(gender="male",max_birth_year=1990)

# 2. Define the event: Heart failure diagnosis (condition_occurrence)
hf_dx = ConditionOccurrence(
    event_concept_id=316139  # Heart failure concept ID
)

# 3. Build the cohort YAML object
cohort = CohortCriteria(
    demographics=demo,
    temporal_blocks=[hf_dx]
)

# 4. Dump YAML file
cohort.save("examples/example2.yaml")
