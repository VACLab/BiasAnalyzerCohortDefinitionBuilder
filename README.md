# BiasAnalyzerCohortDefinitionBuilder

A Python-based package for generating **Cohort definition files** compatible with [BiasAnalyzer](https://github.com/VACLab/BiasAnalyzer).  
It allows researchers to construct complex cohort logic (e.g., temporal relationships, event sequences, logical filters) directly from Python.

---

## Features

- **Event primitives**
  - `ConditionOccurrence` (Dx)
  - `DrugExposure` (Rx)
  - `Measurement` (Labs)
  - `VisitOccurrence` (encounters)
  - `DateEvent` (Fixed calendar dates)
- **Attribute primitives** 
  - `Demographics` (gender, birth year, race, ethnicity)
- **Logical operators**
  - `AND`, `OR`, `NOT` — for Boolean logic  
  - `BEFORE` — for temporal relationships
- **Automatic YAML serialization**  
  Generate ready-to-use `.yaml` cohort definition files directly from Python objects.
- **Flexible schema handling**  
  Fully aligned with BiasAnalyzer’s cohort schema — no structural modifications required.

---

## Project Structure

```text
CohortDefinition/
├── CohortDefinition/
│   ├── __init__.py
│   ├── builder.py              # Core Cohort builder & CohortCriteria class
│   ├── events.py               # Event primitives (Dx, Encounters, etc.)
│   └── logic.py                # Logical & temporal operators
├── examples/
│   ├── build_example1.py
│   ├── build_example2.py
│   ├── build_example3_no_demo.py
│   ├── build_example4_no_temporal.py
│   └── build_example5_not.py
├── setup.py
├── README.md
└── LICENSE
