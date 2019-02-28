# How to execute the unit tests

> tox

This should execute the testsuite with all supported python versions.

# How to send patches

With unit tests please.
Please note that this project practices Semantic Versioning and [Dependable API Evolution](https://github.com/dwt/Dependable_API_Evolution)

# Release checklist
- Tests run at least in python 2.7 and 3.4, 3.5, 3.6, 3.7 (by running tox)
- Increment version and tag
- upload new build with $ rm -r dist/* && ./setup.py sdist bdist_wheel && twine upload dist/*

# Ideas
- Consider to use the call pattern to write the actual error message.
    - could lead to even better wording of the error messages
    - needs to still work reasonable for the operator shortcuts
    - `` expect(foo).to_be.equal_to(bar) `` -> `` Expect <foo> to be equal to <bar> ``
- is there a way to raise the error exception in the context of the parent method, to clean the backtrace even further?
- check that exception chaining is used, so it is easy to get to the original exception with the full stack trace
    - look at sys.settrace and debugger functionality how to do this
- catch up to unittest.Testcase and implement stuff like assertWarns, assertLogs, assertMultiLineEqual
- Generate diffs everywhere to make output more readable
- rework documentation from my talk at berlin.python.pizza
- add sphinx docs that lists all matchers, and especially groups all the alternative names...
- add travis
