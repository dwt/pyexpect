# How to execute the unit tests

> tox

This should execute the testsuite with all supported python versions.

# How to send patches

With unit tests please.

# Release checklist:
- Tests run at least in python 2.7 and 3.4
- Ensure pandoc is installed (to get nicer readme output for pypi)
- Increment version and tag
- upload new build with $ ./setup.py sdist upload
