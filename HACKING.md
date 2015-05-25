# How to execute the unit tests

> tox

This should execute the testsuite with all supported python versions.

# How to send patches

With unit tests please.
Please note that this project practices Semantic Versioning and [Dependable API Evolution](https://github.com/dwt/Dependable_API_Evolution)

# Release checklist
- Tests run at least in python 2.7 and 3.4
- Ensure pandoc is installed (to get nicer readme output for pypi)
- Increment version and tag
- upload new build with $ ./setup.py sdist upload

# Ideas
- Consider to use the call pattern to write the actual error message.
    - could lead to even better wording of the error messages
    - needs to still work reasonable for the operator shortcuts
    - `` expect(foo).to_be.equal_to(bar) `` -> `` Expect <foo> to be equal to <bar> ``
    