from setuptools import setup, find_packages

setup(
    name="BiasAnalyzerYAMLBuilder",
    version="0.1.0",
    description="Schema-faithful helpers to build BiasAnalyzer-compatible cohort YAML.",
    author="Shuhan Lu @ VAC Lab",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=5.4",
    ],
)