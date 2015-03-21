"""
Jasmine compatibility
See: https://github.com/pivotal/jasmine/
"""

def add_jasmine_js_matchers(cls):
    """Modifies the class given to it, if you don't want that, create a local subclass first"""
    # defined is not really a concept that maps well to python
    cls.to_be_defined = cls.exists
    cls.to_be_undefined = cls.is_none
    cls.to_be_null = cls.is_none
    cls.to_be_truthy = cls.is_truthy
    cls.to_be_falsy = cls.is_falsy
    cls.to_contain = cls.contains
    cls.to_be_less_than = cls.less_than
    cls.to_be_greater_than = cls.greater_than
    
    def to_be_close_to(self, expected, max_delta=0.001, precision=None):
        """\
        max_delta defaults to 0.001 which emulates jasmines default precision of 2
        Should you want to work with precisions instead of deltas, you need to specify
        that explicitly.
        """
        if precision is None:
            return self.close_to(expected, max_delta=max_delta)
        else:
            max_delta = (10.0 ** -precision) / 2
            actual_delta = abs(expected - self._actual)
            self._assert(actual_delta < max_delta, "to be close to {0!r} with {1!r} matching digits (actual_delta={2!r}, expected_delta={3!r})", expected, precision, actual_delta, max_delta)
    cls.to_be_close_to = to_be_close_to
