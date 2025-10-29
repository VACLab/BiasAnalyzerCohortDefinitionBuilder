"""
Example 4: Demographics only: female, born between 2000 and 2020 (inclusive).
"""

from CohortDefinition import Demographics, CohortCriteria

demo = Demographics(
    gender="female",
    min_birth_year=2000,
    max_birth_year=2020,
)

cohort = CohortCriteria(demographics=demo)

cohort.save("examples/example4.yaml")
