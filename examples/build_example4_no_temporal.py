"""
Example 5: Demographics only: female, born between 2000 and 2020 (inclusive).
"""

from python_to_YAML import Demographics, CohortYAML

demo = Demographics(
    gender="female",
    min_birth_year=2000,
    max_birth_year=2020,
)

cohort = CohortYAML(demographics=demo)

cohort.dump_yaml("examples/example4.yaml")
