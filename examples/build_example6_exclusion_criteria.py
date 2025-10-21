"""
Example 6: Inclusion + Exclusion criteria
- Inclusion: Type 2 Diabetes
- Exclusion: Heart Failure
Shows how to populate 'exclusion_criteria' alongside 'inclusion_criteria'.
"""
from python_to_YAML import ConditionOccurrence, Demographics, CohortYAML

# Optional demographics on inclusion side
demo = Demographics(gender="male")

# Inclusion: T2DM (example OMOP concept id)
t2dm = ConditionOccurrence(event_concept_id=201826)

# Exclusion: Heart failure
hf = ConditionOccurrence(event_concept_id=316139)

# Build with both sides; relies on new 'exclusion_blocks' support in CohortYAML
cohort = CohortYAML(
    demographics=demo,
    temporal_blocks=[t2dm],     # inclusion
    exclusion_blocks=[hf],      # exclusion
)
cohort.save_yaml("examples/example6.yaml")