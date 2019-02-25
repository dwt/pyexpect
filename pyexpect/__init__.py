#!/usr/bin/env python
# encoding: utf8

# ISC Licensed <https://opensource.org/licenses/ISC>
# Author: Martin Häcker mhaecker ät mac dot com

# Inspired by:
# Rubys RSpec that got me longing for a similar syntax
# Robert who suggested lots of great api ideas

# TODO: 
# - Ensure no matcher disapears during an update
# - get build server + button on bitbucket
# - get coverage + button on bitbucket
# - get documentation + button on bitbucket
# - allow subexpects, i.e. matchers that are implemented in terms of other matchers
# - allow adding negation as a parameter to expect

__all__ = ['expect']

import re, sys, numbers
from .internals import ExpectMetaMagic, alias_with_hidden_backtrace

marker = object()

class expect(ExpectMetaMagic):
    """Minimal but very flexible implementation of the expect pattern.
    
    Use like this:
    
        expect('foo').to.equal('bar')
    
    To get error messages like this:
    
        Expect 'foo' to equal 'bar'.
    
    Most usefull in unit and acceptance tests but also as general assertions throughout your code.
    
    To add custom matchers, either subclass expect and add them as instance methods, or just add 
    them as instance methods to the expect object:
    
        def my_matcher(self, arguments, defaults='something):
            pass # whatever you have to do. For helpers and availeable values see dir(expect())
        expect.new_matcher = my_matcher
    
    If you want the expectation to return a bool instead of raising go for:
    
        a_bool, error_message = expect.returning(something).then.call.a.matcher()
    
    For more options and a list of the matchers, see the source. :)
    """
    
    def __init__(self, actual, should_raise=True, message=None):
        """Initialize a useable assertion object that you can chain off of.
        
        should_raise=False
            will toggle the behavior of the assertion to return a tuple
            (boolean, string) instead of raising an AssertionError or not raising
        
        message
            can be a custom message that replaces the original message in case of error.
            You can include the original message with the format `{assertion_message}` in 
            your message. For more details see the source of self._message()
        """
        self._actual = actual
        self._should_raise = should_raise
        self._custom_message = message
        self._expected_assertion_result = True
        self._selected_matcher = None
        self._selected_matcher_name = None
    
    @classmethod
    def with_message(cls, message, actual, should_raise=True):
        """Convenience method to specify a custom message to expect()
        
        Works like the regular expect(), but instead of the error message from the matcher,
        the provided `message` will be used.
        
        You can include the original message with the format `{assertion_message}` in 
        your message. For more details see the source of self._message()
        """
        return cls(actual, message=message, should_raise=should_raise)
    
    @classmethod
    def returning(cls, actual, message=None):
        """Convenience method for a non raising expect()
        
        Works like a regular expect(), but instead of raising AssertionError it returns
        a (boolean, string) tupple that contains the expectation result and either the empty string
        or the Expectation message that would have been on the AssertionError.
        
        To get a callable reuseable expectation, use it like this:
        
            an_expectation = lambda actual: expect.returning(actual).to_be('fnord')
        """
        return cls(actual, should_raise=False, message=message)
    
    ## Matchers #########################################################################################
    
    # All public methods on this class are expected to be matchers.
    # Beware the consequences if you break this promise. :)
    
    # On writing matchers:
    # You really only need to throw an AssertionError from the matcher and you're done.
    # However, you should always use the self._assert* family of methods to do so, to support automatic negation, and nice error message enhancement.
    
    # On naming matchers:
    # Their name should be clear and fit in with the naming scheme of the existing matchers. 
    # That is: short and active if possible. Matcher names should fullfill two roles. 
    # They should allow direct usage, without chaining in front of them:
    #    expect(3).equals(3)
    # They should also allow chaining to read more like a sentence:
    #    expect(3).to.equal(3)
    #    expect(3).is_.equal(3)
    # If sensible, also support an operator overloaded forms:
    #    expect(3) == 3
    # The goal is to allow the code to read sensible and as similar to the generated error message as possible.
    # Include as many alternative names as make sense.
    
    # Right now some be_* prefixes are included as aliasses, but I will probably phase 
    # them out in favor of using arbitrary chaining to achieve their effect.
    
    # On debugging matchers:
    # Some pyton debuggers will hide all the internals of the expect method
    # To match py.tests behaviour. Read up on hidden frames and how to unhide them in your python debugger
    # `hf_unhide` is often the keyword here.
    # It can also be helpfull to disable the backtrace munging that pyexpect does. 
    # To do so, wrap the code in question with:
    #    import pyexpect.internals
    #    with expect.internals.disabled_backtrace_cleaning():
    #        expect(foo).my_matcher()
    # and you will get the full traceback.

    
    def true(self):
        self._assert(self._actual is True, "to be True")
    
    is_true = true
    
    def false(self):
        self._assert(self._actual is False, "to be False")
    
    is_false = false
    
    def none(self):
        self._assert(self._actual is None, "to be None")
    
    is_none = to_be_none = none

    def exist(self):
        self._assert(self._actual is not None, "to exist (not be None)")
    
    exists = to_exist = exist
    
    # REFACT: consider adding 'from' alias to allow syntax like expect(False).from(some_longish_expression())
    # Could enhance readability, not sure it's a good idea?
    def equal(self, something):
        self._assert(something == self._actual, "to equal {0!r}", something)
    
    equals = equal
    to_equal = is_equal = equal
    __eq__ = alias_with_hidden_backtrace('equal')
    
    def different(self, something):
        self.not_ == something
    
    is_different = different
    __ne__ = alias_with_hidden_backtrace('different')
    
    def change(self, getter, from_=marker, by=None, to=marker):
        """@arg from_ and @arg to can be of any type.
        @arg by only supports numeric arguments right now and requires
        @arg from_ and @arg to also to be numeric."""
        # REFACT how to make this usefull with floats maybe a similar but different matcher?
        expect(self._actual).is_callable()
        expect(getter).is_callable()
        expect(
            from_ is not marker
            or by is not None
            or to is not marker,
            message="At least one argument of 'from_', 'by', 'to' has to be specified"
        ).is_true()
        
        if by is not None:
            expect(by).is_instance_of(numbers.Number)    
            if to is not marker: expect(to).is_instance_of(numbers.Number)
            if from_ is not marker: expect(from_).is_instance_of(numbers.Number)
            if to is not marker and from_ is not marker:
                assert from_ + by == to, \
                    "Inconsistant arguments: from={from_!r} + by={by!r} != to={to!r}".format(**locals())
        
        before = getter()
        self._actual()
        after = getter()
        
        if by is not None:
            message = "by={by!r} was given, but getter did not return a numeric value".format(**locals())
            expect(before, message=message).is_instance_of(numbers.Number)
            expect(after, message=message).is_instance_of(numbers.Number)
        
        # REFACT consider to assert that before and after have to be numeric if by is given
        def assertion():
            by_ok =  before + by == after if by is not None else True
            from_ok = before == from_ if from_ is not marker else True
            to_ok = after == to if to is not marker else True
            return by_ok and from_ok and to_ok
        
        def message():
            # only outputs the first error, as that works way better with negated answers.
            # TODO would be nice to find a formulation that allows showing all errors at once
            message = ""
            if from_ is not marker:
                message += 'to start from {from_!r} '
            elif by is not None:
                message += 'to change by {by!r} '
            elif to is not marker:
                message += 'to end with {to!r} '
            return message + 'but it changed from {before!r} to {after!r}'
        
        self._assert(assertion(), message(), \
            from_=from_, to=to, by=by, before=before, after=after)
    
    changing = changes = change
    is_changing = to_change = change
    
    def be(self, something):
        self._assert(something is self._actual, "to be {0!r}", something)
    
    same = identical = is_ = be
    be_same = is_same = be_identical = is_identical = is_identical_to = to_be = be
    
    def trueish(self):
        self._assert(bool(self._actual) is True, "to be trueish")
    
    truthy = truish = trueish
    is_trueish = trueish
    is_truthy = truthy
    
    def falseish(self):
        self._assert(bool(self._actual) is False, "to be falseish")
    
    falsy = falsish = falseish
    is_falseish = falseish
    is_falsy = falsy
    
    def includes(self, needle, *additional_needles):
        for needle in self._concatenate(needle, *additional_needles):
            self._assert(needle in self._actual, "to include {0!r}", needle)
    
    contain = contains = include = includes
    to_contain = does_include = to_include = has_key = includes
    
    def within(self, sequence_or_atom, *additional_atoms):
        sequence = sequence_or_atom
        if len(additional_atoms) > 0:
            sequence = self._concatenate(sequence_or_atom, *additional_atoms)
        
        self._assert(self._actual in sequence, "is included in {0!r}", sequence)
    
    in_ = included_in = within
    is_within = is_included_in = within
    
    # REFACT: Error message is hard to read., needs formatting on multiple lines, or restriction to just the keys in question. Consider using pprint to format the output better?
    def sub_dict(self, a_subdict=None, **kwargs):
        expect(self._actual).is_instance(dict)
        
        if a_subdict is None:
            a_subdict = dict()
        a_subdict.update(kwargs)
        
        expected_keys = a_subdict.keys()
        expected_items = list(a_subdict.items())
        actual_items = [(key, self._actual.get(key)) for key in expected_keys]
        # superset = set(self._actual.iteritems())
        # REFACT: subset.issubset(superset)
        self._assert(actual_items == expected_items, 'to contain dict {0!r}', a_subdict)
    
    includes_dict = contains_dict = subdict = sub_dict
    to_have_subdict = have_subdict = have_sub_dict = has_subdict = has_sub_dict = sub_dict
    
    def sub_list(self, sequence_or_atom, *additional_atoms):
        sequence = sequence_or_atom
        if len(additional_atoms) > 0:
            sequence = self._concatenate(sequence_or_atom, *additional_atoms)
        def includes_sequence():
            if len(sequence) > len(self._actual):
                return False
            normalized_sequence = tuple(sequence)
            for start in range(len(self._actual) - len(sequence) + 1):
                if tuple(self._actual[start:start+len(sequence)]) == normalized_sequence:
                    return True
            return False
        self._assert(includes_sequence(), "to contain sequence {0!r}", sequence)
    to_have_sub_sequence = has_sub_sequence = sub_sequence = sub_list
    to_have_sublist = to_have_sub_list = has_sublist = has_sub_list = sub_list
    
    def has_attribute(self, *attribute_names, **attributes):
        for attribute_name in attribute_names:
            self._assert(hasattr(self._actual, attribute_name), "to have attribute {0!r}", attribute_name)
        
        if len(attributes) >= 1:
            missing_attribute = object()
            actual_attributes = dict(
                (attribute_name, getattr(self._actual, attribute_name, missing_attribute))
                for attribute_name, attribute_value in attributes.items()
            )
            self._assert(actual_attributes == attributes,
                'to have attributes {0!r}, \n\tbut has {1!r}', 
                attributes, actual_attributes)
    hasattr = has_attr = has_attribute
    have_attribute = have_attr = has_attribute
    have_attribues = has_attributes = have_attrs = has_attribute
    to_have_attributes = has_attribute
    
    def matches(self, regex):
        string_type = str if sys.version > '3' else basestring
        expect(self._actual).is_instance(string_type)
        
        self._assert(re.search(regex, self._actual) is not None, "to be matched by regex r{0!r}", regex)
    
    match = matching = matches
    is_matching = to_match = matches
    
    def starts_with(self, expected_start):
        self._assert(self._actual.startswith(expected_start), "to start with {0!r}", expected_start)
    
    startswith = to_start_with = starts_with
    
    def ends_with(self, expected_end):
        self._assert(self._actual.endswith(expected_end), "to end with {0!r}", expected_end)
    
    endswith = to_end_with = ends_with
    
    # TODO: consider with statement support to allow code like this
    # with expect.raises(AssertionError):
    #   something.that_might_raise()
    def to_raise(self, exception_class=Exception, message_regex=None):
        """ Check regexes by type and an optional message.
        
        Example:
        catched_regex = expect(lambda: some_call(arg)).raises(SomeError)
        catched_regex = expec(lambda: some_call(arg)).raises(SomeError, "a regex for the message")
        
        Always returns the exception that is caught.
        
        Exceptions that are not expected are rethrown, especially in negative cases.
        """
        # REFACT: consider to change to_raise to let all unexpected exceptions pass through
        # Not sure what that means to correctly implement the negative side though
        expect(self._actual).is_callable()
        
        caught_exception = None
        traceback = None
        try:
            self._actual()
            # REFACT: consider to catch exception_class instead?
        except BaseException as exception:
            caught_exception = exception
            _, _, traceback = sys.exc_info()
        
        is_right_class = isinstance(caught_exception, exception_class)
        if message_regex is None:
            self._assert(is_right_class, 
                "to raise {0} but it raised:\n\t{1!r}", exception_class.__name__, caught_exception)
        else:
            has_matching_message = re.search(message_regex, str(caught_exception)) is not None
            self._assert(is_right_class and has_matching_message, 
                "to raise {0} with message matching:\n\tr'{1}'\nbut it raised:\n\t{2!r}", 
                exception_class.__name__, message_regex, caught_exception)
        
        if self._is_negative() and caught_exception:
            if sys.version < '3':
                exec("raise caught_exception, None, traceback")
            else:
                raise caught_exception
        
        return caught_exception
    
    throw = throwing = throws = raise_ = raising = raises = to_raise
    is_raising = is_throwing = to_throw = to_raise
    
    def empty(self):
        self._assert(len(self._actual) == 0, "to be empty")
    
    is_empty = to_be_empty = empty
    
    def instance_of(self, a_class, *additional_classes):
        for cls in self._concatenate(a_class, *additional_classes):
            self._assert(isinstance(self._actual, cls), "to be instance of '{0}'", a_class.__name__)
    
    isinstance = instanceof = instance_of
    is_instance = is_instance_of = instance_of
    
    def is_subclass_of(self, a_superclass, *addition_superclasses):
        for superclass in self._concatenate(a_superclass, *addition_superclasses):
            self._assert(issubclass(self._actual, superclass), "to be subclass of {0!r}", a_superclass)
    
    issubclass = is_subclass = subclass_of = subclass = is_subclass_of
    
    def is_callable(self):
        self._assert(callable(self._actual) is True, "to be callable")
    
    callable = is_callable
    
    def length(self, a_length):
        actual = len(self._actual)
        self._assert(actual == a_length, "to have length {0}, but found length {1}", a_length, actual)
    
    len = count = length
    has_len = have_length = has_count = has_length = length
    
    def greater_than(self, smaller):
        self._assert(self._actual > smaller, "to be greater than {0!r}", smaller)
    
    bigger = larger = larger_than = greater = greater_than
    is_greater_than = is_greater = greater_than
    __gt__ = alias_with_hidden_backtrace('greater_than')
    # TODO: consider to include *_then because it's such a common error?
    
    def greater_or_equal(self, smaller_or_equal):
        self._assert(self._actual >= smaller_or_equal, "to be greater or equal than {0!r}", smaller_or_equal)
    
    greater_or_equal_than = greater_or_equal
    is_greater_or_equal_than = is_greater_or_equal = greater_or_equal
    __ge__ = alias_with_hidden_backtrace('greater_or_equal')
    # TODO: consider to include *_then because it's such a common error?
    
    def less_than(self, greater):
        self._assert(self._actual < greater, "to be less than {0!r}", greater)
    
    smaller = smaller_than = lesser = lesser_than = less = less_than
    is_smaller_than = is_less_than = less_than
    __lt__ = alias_with_hidden_backtrace('less_than')
    # TODO: consider to include *_then because it's such a common error?
    
    def less_or_equal(self, greater_or_equal):
        self._assert(self._actual <= greater_or_equal, "to be less or equal than {0!r}", greater_or_equal)
    
    smaller_or_equal = smaller_or_equal_than = lesser_or_equal = lesser_or_equal_than = less_or_equal_than = less_or_equal
    is_smaller_or_equal = is_smaller_or_equal_than = is_less_or_equal_than = is_less_or_equal = less_or_equal
    __le__ = alias_with_hidden_backtrace('less_or_equal')
    # TODO: consider to include *_then because it's such a common error?
    
    # TODO: consider adding is_between_exclusive
    # TODO: consider supporting slice syntax as alias. expect(3)[2:4] doesn't look natural though
    # REFACT: consider to change to be more like range(), i.e. lower bound included, upper bound excluded
    # Alternative: add in_range that includes lower bound but excludes upper one
    # REFACT: name could also reflect better that between actually includes both ends of the range
    # Alternatives: in_open_range, within_half_closed_range, within_range_including_lower_bound
    def between(self, lower, higher):
        self._assert(lower <= self._actual <= higher, "to be between {0!r} and {1!r}", lower, higher)
    
    within_range = between
    is_within_range = is_between = between
    
    def close_to(self, expected, max_delta):
        self._assert((expected - max_delta) <= self._actual <= (expected + max_delta), "to be close to {0!r} with max delta {1!r}", expected, max_delta)
    
    about_equals = about_equal = about = almost_equals = almost_equal = close = close_to
    is_about =  is_almost_equal = is_close = is_close_to = close_to
    
    def is_permutation_of(self, a_sequence, *additional_elements):
        def element_counts(a_sequence):
            import collections
            counts = collections.defaultdict(int)
            for element in a_sequence:
                counts[element] += 1
            return counts
        
        self._assert(element_counts(self._actual) == element_counts(a_sequence), "to be permutation of {0!r}", a_sequence)
        
