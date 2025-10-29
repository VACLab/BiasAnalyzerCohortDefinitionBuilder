# example 8: Patients over 65 who have been diagnosed with multiple myeloma (C90.0) or plasma cell leukemia (C90.1), 
# gather data for 2 years prior to initial diagnosis and 2 years after.

from CohortDefinition import (
    ConditionOccurrence, Demographics, CohortCriteria, OR, AND
)

# Demographics: Born ≤ 1960
demo = Demographics(max_birth_year=1960)

# ---------- Group A: OR of initial Dx 2 years prior (offset = -730) ----------
mm_prior   = ConditionOccurrence(event_concept_id=437233, event_instance=1, offset=-730)  # Multiple myeloma
pcl_prior  = ConditionOccurrence(event_concept_id=133154, event_instance=1, offset=-730)  # Plasma cell leukemia
group_A = OR(mm_prior, pcl_prior)  # strictly binary

# ---------- Group B: OR of initial Dx 2 years after (offset = +730) ----------
mm_after   = ConditionOccurrence(event_concept_id=437233, event_instance=1, offset=730)
pcl_after  = ConditionOccurrence(event_concept_id=133154, event_instance=1, offset=730)
group_B = OR(mm_after, pcl_after)  # strictly binary

# ---------- Top-level AND over the two OR groups ----------
rule = AND(group_A, group_B)  # strictly binary

cohort = CohortCriteria(
    demographics=demo,
    temporal_blocks=[rule],   # single operator block → 原样进 temporal_events
)

cohort.save("examples/example8.yaml")
#print(cohort.to_yaml(sort_keys=False))
print(cohort.to_yaml())
