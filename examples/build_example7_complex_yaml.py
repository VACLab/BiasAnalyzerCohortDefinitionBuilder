"""
Example 7 (final): Two parallel temporal groups, with an AND subgroup that contains two BEFOREs.

inclusion_criteria.temporal_events:
  [0] OR group (visits only; no interval):
      events:
        - visit_occurrence, concept_id=9201, event_instance=2
        - visit_occurrence, concept_id=9203
  [1] BEFORE group (with interval [2, 5]):
      events:
        - condition_occurrence, concept_id=4041664
        - AND subgroup of TWO BEFOREs:
            a) BEFORE(date '2020-03-15', COVID 37311061)
            b) BEFORE(COVID 37311061, date '2020-12-11')

exclusion_criteria: (placeholder—replace to match teacher’s exact block if needed)
"""

from CohortDefinition import (
    ConditionOccurrence,
    VisitOccurrence,
    DateEvent,
    Demographics,
    CohortCriteria,
    OR,
    AND,
    BEFORE,
)

# ---------------- Demographics ----------------
demo_incl = Demographics(gender="female", min_birth_year=2000, max_birth_year=2020)

# ---------------- Group [0]: OR over two visit_occurrence leaves ---------------------------
ip_2nd = VisitOccurrence(event_concept_id=9201, event_instance=2)
er     = VisitOccurrence(event_concept_id=9203)
group0 = OR(ip_2nd, er)  # strict binary OR

# ---------------- Group [1]: BEFORE + interval; right operand is AND of two BEFOREs --------
lhs_dyspnea = ConditionOccurrence(event_concept_id=4041664)     # leaf: difficulty breathing
covid       = ConditionOccurrence(event_concept_id=37311061)     # leaf: COVID

# two boundaries as BEFOREs (strict binary)
start_date  = DateEvent(timestamp="2020-03-15")
end_date    = DateEvent(timestamp="2020-12-11")
bound_left  = BEFORE(start_date, covid)   # date_start BEFORE covid
bound_right = BEFORE(covid, end_date)     # covid BEFORE date_end

# AND subgroup contains exactly TWO BEFORE blocks (strict binary AND)
date_window_and = AND(bound_left, bound_right)

# Outer BEFORE (strict binary): dyspnea BEFORE (AND of [date_start BEFORE covid, covid BEFORE date_end])
group1 = BEFORE(lhs_dyspnea, date_window_and)
group1["interval"] = [2, 5]               # keep the 2–5 day window on the OUTER BEFORE

# ---------------- Exclusion criteria (placeholder; align to teacher sample if different) ----
demo_excl = Demographics(min_birth_year=2010)
hf_excl   = ConditionOccurrence(event_concept_id=316139)

# ---------------- Build & Save --------------------------------------------------------------
cohort = CohortCriteria(
    demographics=demo_incl,
    temporal_blocks=[group0, group1],         # TWO parallel temporal groups
    exclusion_demographics=demo_excl,
    exclusion_blocks=[hf_excl],
)

cohort.save("examples/example7.yaml")
#print(cohort.to_yaml(sort_keys=False))
