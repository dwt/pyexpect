#!/usr/bin/env python
# encoding: utf8

# BSD Licensed <http://opensource.org/licenses/BSD-2-Clause>
# Author: Martin Häcker mhaecker ät mac dot com

# Inspired by:
# Rubys RSpec that got me longing for a similar syntax
# Robert who suggested lots of great api ideas

# TODO: 
# - Ensure no matcher disapears during an update
# - get build server + button on bitbucket
# - get coverage + button on bitbucket
# - get documentation + button on bitbucket
# Improve py3 support - shorten exception stack traces

__all__ = ['expect']

import re, sys

class expect(object):
    """Minimal but very flexible implementation of the expect pattern.
    
    Use like this:
    
        expect('foo').to.equal('bar')
    
    To get error messages like this:
    
        Expect 'foo' to equal 'bar'.
    
    Most usefull in unit and acceptance tests but also as general assertions throughout your code.
    
    To add custom matchers, just add them as instance methods to the expect object:
    
        def my_matcher(self, arguments, defaults='something):
            pass # whatever you have to do. For helpers and availeable values see dir(expect())
        expect.new_matcher = my_matcher
    
    If you want the expectation to return a bool instead of raising go for:
    
        a_bool, error_message = expect.returning(somethign).then.call.a.matcher()
    
    For more options and a list of the matchers, see the source. :)
    """
    
    def __init__(self, expected, should_raise=True, message=None):
        """Initialize a useable assertion object that you can chain off of.
        
        should_raise=False
            will toggle the behavior of the assertion to return a tuple
            (boolean, string) instead of raising an AssertionError or not raising
        
        message
            can be a custom message that replaces the original message in case of error.
            You can include the original message with the format `{assertion_message}` in 
            your message. For more details see the source of self._message()
        """
        self._expected = expected
        self._should_raise = should_raise
        self._custom_message = message
        self._expected_assertion_result = True
        self._selected_matcher = None
        self._selected_matcher_name = None
        
        self._enable_nicer_backtraces_for_new_double_underscore_matcher_alternatives()
    
    @classmethod
    def with_message(cls, message, expected, should_raise=True):
        """Convenience method to specify a custom message to expect()
        
        Works like the regular expect(), but instead of the error message from the matcher,
        the provided `message` will be used.
        
        You can include the original message with the format `{assertion_message}` in 
        your message. For more details see the source of self._message()
        """
        return cls(expected, message=message, should_raise=should_raise)
    
    @classmethod
    def returning(cls, expected, message=None):
        """Convenience method for a non raising expect()
        
        Works like a regular expect(), but instead of raising AssertionError it returns
        a (boolean, string) tupple that contains the expectation result and either the empty string
        or the Expectation message that would have been on the AssertionError.
        
        To get a callable reuseable expectation, use it like this:
        
            an_expectation = lambda expected: expect.returning(expected).to_be('fnord')
        """
        return cls(expected, should_raise=False, message=message)
    
    ## Matchers #########################################################################################
    
    # All public methods on this class are expected to be matchers.
    # Beware the consequences if you break this promise. :)
    
    # On writing matchers:
    # You really only need to throw an AssertionError from the matcher and you're done.
    # However, you should always use the self._assert* family of methods to do so, to support automatic negation.
    
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
    
    # On debugging matchers: Some pyton debuggers will hide all the internals of the expect method
    # To match py.tests behaviour. Read up on hidden frames and how to unhide them in your python debugger
    # `hf_unhide` is often the keyword here.
    
    def true(self):
        self._assert(self._expected is True, "to be True")
    
    is_true = true
    
    def false(self):
        self._assert(self._expected is False, "to be False")
    
    is_false = false
    
    def none(self):
        self._assert(self._expected is None, "to be None")
    
    is_none = none
    
    def exist(self):
        self._assert(self._expected is not None, "to exist (not be None)")
    
    exists = exist
    # REFACT: consider adding 'from' alias to allow syntax like expect(False).from(some_longish_expression())
    # Could enhance readability, not sure it's a good idea?
    def equal(self, something):
        self._assert(something == self._expected, "to equal {0!r}", something)
    
    __eq__ = equals = equal
    to_equal = is_equal = equal
    
    def different(self, something):
        self.not_ == something
    
    __ne__ = different
    is_different = different
    
    def be(self, something):
        self._assert(something is self._expected, "to be {0!r}", something)
    
    same = identical = is_ = be
    be_same = is_same = be_identical = is_identical = to_be = be
    
    def trueish(self):
        self._assert(bool(self._expected) is True, "to be trueish")
    
    truthy = truish = trueish
    is_trueish = trueish
    
    def falseish(self):
        self._assert(bool(self._expected) is False, "to be falseish")
    
    falsy = falsish = falseish
    is_falseish = falseish
    
    def includes(self, needle, *additional_needles):
        for needle in [needle] + list(additional_needles):
            self._assert(needle in self._expected, "to include {0!r}", needle)
    
    contain = contains = include = includes
    does_include = to_include = has_key = includes
    
    def within(self, sequence_or_atom, *additional_atoms):
        sequence = sequence_or_atom
        if len(additional_atoms) > 0:
            sequence = [sequence_or_atom]
            sequence.extend(additional_atoms)
        
        self._assert(self._expected in sequence, "is included in {0!r}", sequence)
    
    in_ = included_in = within
    is_within = is_included_in = within
    
    def sub_dict(self, a_subdict=None, **kwargs):
        expect(self._expected).is_instance(dict)
        
        if a_subdict is None:
            a_subdict = dict()
        a_subdict.update(kwargs)
        
        actual_keys = a_subdict.keys()
        actual_items = list(a_subdict.items())
        expected_items = [(key, self._expected.get(key)) for key in actual_keys]
        # superset = set(self._expected.iteritems())
        # REFACT: subset.issubset(superset)
        self._assert(expected_items == actual_items, 'to contain dict {0!r}', a_subdict)
    
    includes_dict = contains_dict = subdict = sub_dict
    have_subdict = have_sub_dict = has_subdict = has_sub_dict = sub_dict
    
    def to_match(self, regex):
        string_type = str if sys.version > '3' else basestring
        expect(self._expected).is_instance(string_type)
        
        self._assert(re.search(regex, self._expected) is not None, "to be matched by regex r{0!r}", regex)
    
    match = matching = matches = to_match
    is_matching = to_match
    
    # TODO: consider with statement support to allow code like this
    # with expect.raises(AssertionError):
    #   something.that_might_raise()
    def to_raise(self, exception_class=Exception, message_regex=None):
        """Be carefull with negative raise assertions as they swallow all exceptions that you 
        don't specify. If you say `expect(raiser).not_.to_raise(FooException, 'fnord')` this 
        is interpreted as: every other exception that doesn't conform to this description is 
        ok and expected.
        """
        # REFACT: consider to change to_raise to let all unexpected exceptions pass through
        # Not sure what that means to correctly implement the negative side though
        expect(self._expected).is_callable()
        
        caught_exception = None
        try:
            self._expected()
        except BaseException as exception:
            caught_exception = exception
        
        is_right_class = isinstance(caught_exception, exception_class)
        if message_regex is None:
            self._assert(is_right_class, 
                "to raise {0} but it raised:\n\t{1!r}", exception_class.__name__, caught_exception)
        else:
            has_matching_message = re.search(message_regex, str(caught_exception)) is not None
            self._assert(is_right_class and has_matching_message, 
                "to raise {0} with message matching:\n\tr'{1}'\nbut it raised:\n\t{2!r}", 
                exception_class.__name__, message_regex, caught_exception)
        
        return caught_exception
    
    throw = throwing = throws = raise_ = raising = raises = to_raise
    is_raising = is_throwing = to_raise
    
    def empty(self):
        self._assert(len(self._expected) == 0, "to be empty")
    
    is_empty = empty
    
    def instance_of(self, a_class):
        self._assert(isinstance(self._expected, a_class), "to be instance of '{0}'", a_class.__name__)
    
    isinstance = instanceof = instance_of
    is_instance = is_instance_of = instance_of
    
    def is_callable(self):
        self._assert(callable(self._expected) is True, "to be callable")
    
    callable = is_callable
    
    def length(self, a_length):
        actual = len(self._expected)
        self._assert(actual == a_length, "to have length {0}, but found length {1}", a_length, actual)
    
    len = count = length
    has_count = has_length = length
    
    def greater_than(self, smaller):
        self._assert(self._expected > smaller, "to be greater than {0!r}", smaller)
    
    __gt__ = bigger = larger = larger_than = greater = greater_than
    is_greater_than = is_greater = greater_than
    # TODO: consider to include *_then because it's such a common error?
    
    def greater_or_equal(self, smaller_or_equal):
        self._assert(self._expected >= smaller_or_equal, "to be greater or equal than {0!r}", smaller_or_equal)
    
    __ge__ = greater_or_equal_than = greater_or_equal
    is_greater_or_equal_than = is_greater_or_equal = greater_or_equal
    # TODO: consider to include *_then because it's such a common error?
    
    def less_than(self, greater):
        self._assert(self._expected < greater, "to be less than {0!r}", greater)
    
    __lt__ = smaller = smaller_than = lesser = lesser_than = less = less_than
    is_smaller_than = is_less_than = less_than
    # TODO: consider to include *_then because it's such a common error?
    
    def less_or_equal(self, greater_or_equal):
        self._assert(self._expected <= greater_or_equal, "to be less or equal than {0!r}", greater_or_equal)
    
    __le__ = smaller_or_equal = smaller_or_equal_than = lesser_or_equal = lesser_or_equal_than = less_or_equal_than = less_or_equal
    is_smaller_or_equal = is_smaller_or_equal_than = is_less_or_equal_than = is_less_or_equal = less_or_equal
    # TODO: consider to include *_then because it's such a common error?
    
    # TODO: consider adding is_between_exclusive
    # TODO: consider supporting slice syntax as alias. expect(3)[2:4] doesn't look natural though
    # REFACT: consider to change to be more like range(), i.e. lower bound included, upper bound excluded
    # Alternative: add in_range that includes lower bound but excludes upper one
    # REFACT: name could also reflect better that between actually includes both ends of the range
    # Alternatives: in_open_range, within_half_closed_range, within_range_including_lower_bound
    def between(self, lower, higher):
        self._assert(lower <= self._expected <= higher, "to be between {0!r} and {1!r}", lower, higher)
    
    within_range = between
    is_within_range = is_between = between
    
    def close_to(self, actual, max_delta):
        self._assert((actual - max_delta) <= self._expected <= (actual + max_delta), "to be close to {0!r} with max delta {1!r}", actual, max_delta)
    
    about_equals = about_equal = about = almost_equals = almost_equal = close = close_to
    is_about =  is_almost_equal = is_close = is_close_to = close_to
    
    ## Internals ########################################################################################
    
    def __getattribute__(self, name):
        """Allows you to chain any python identifier to this object and keep 
        chaining for as long as you want as syntactic sugar.
        
        Only the last identifier that is then actually called has to be an actual 
        matcher.
        
        Including 'not' in any of the identifiers used in chaining will invert the 
        whole expectation. This includes calling the negated form of a matcher by 
        prefixing it with not_ like 'not_to_be' to get the inverted form of 'to_be'.
        """
        # Allow normal access to everything that is not a matcher. 
        # (Every public method is treated as a matcher)
        # REFACT: I would prefer it if not every access to private methods would go through this method
        # However as I do not want to return instance methods and other existing methods directly, there
        # seems to be no way to do this.
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        
        # If you include not somewhere in the called attributes name, 
        # switch the expectation to negative.
        if name.startswith('not_') or '_not_' in name or name.endswith('_not'):
            self._expected_assertion_result = False
        
        self._prepare_matcher_for_calling(name, self._matcher_with_name(name))
        
        # Allow arbitrary chaining
        return self
    
    def _matcher_with_name(self, name):
        # REFACT: consider to change matcher lookup to allow some more pre- and suffixes
        # could be be_ to_ and some more to dry up the list of alternative names that have 
        # to be written out for each matcher.
        if name.startswith('not_'):
            name = name[4:]
        
        # need object.__getattribute__ to prevent recursion with self.__getattribute__
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            return None
    
    def _prepare_matcher_for_calling(self, name, matcher):
        self._selected_matcher_name = name
        self._selected_matcher = matcher
    
    def __call__(self, *args, **kwargs):
        """Called whenever you actualy invoke a matcher. 
        
        Provides a good error message if you mistype the matcher name.
        
        Supports custom messages with the message keyword argument"""
        __tracebackhide__ = True  # Hide from py.test tracebacks
        
        if self._selected_matcher is None:
            # REFACT: consider raising NotImplementedError
            raise AssertionError("Tried to call non existing matcher '{0}' (Patches welcome!)".format(self._selected_matcher_name))
        
        try:
            return_value = self._selected_matcher(*args, **kwargs)
            # allow an otherwise raising matcher to return something
            # usefull for matchers like expect.to_raise() to return the caught exception for further analysis
            if self._should_raise:
                return return_value
        except AssertionError as assertion:
            message = self._message(assertion)
            
            if self._should_raise:
                # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
                # Hides the actual matcher and all the methods it calls to assert stuff.
                raise AssertionError(message)
            
            return (False, message)
        
        return (True, "")
    
    def _assert(self, assertion, message_format, *message_positionals, **message_keywords):
        assert assertion is self._expected_assertion_result, \
            message_format.format(*message_positionals, **message_keywords)
    
    def _assert_if_positive(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._is_negative():
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _assert_if_negative(self, assertion, message_format, *message_positionals, **message_keywords):
        if not self._is_negative():
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _message(self, assertion):
        message = self._message_from_assertion(assertion)
        expected = self._expected
        optional_negation = ' not ' if self._is_negative() else ' '
        assertion_message = "Expect {expected!r}{optional_negation}{message}".format(**locals())
        
        if self._custom_message is not None:
            return self._custom_message.format(**locals())
        
        return assertion_message
    
    def _message_from_assertion(self, assertion):
        if sys.version < '3':
            try: return unicode(assertion).encode('utf8')
            except UnicodeDecodeError as ignored: pass
        
        return str(assertion)
    
    def _is_negative(self):
        return self._expected_assertion_result is False
    
    @classmethod
    def _enable_nicer_backtraces_for_new_double_underscore_matcher_alternatives(cls):
        """Works around the problem that special methods (as in '__something__') are not resolved
        using __getattribute__() and thus do not provide the nice tracebacks that they public matchers provide.
        
        This method works on the class dict and is repeated after each instantiation
        to support adding or overwriting existing matchers at any time while not repeatedly doing the same.
        """
        # TODO: try if turning the special methods into descriptors allows to trigger
        # self.__getattribute__() without increasing the stack trace length on failures
        def wrap(special_method_name, public_name):
            def wrapper(self, *args, **kwargs):
                __tracebackhide__ = True  # Hide from py.test tracebacks
                # Sadly this increases the traceback lenght by one entry for other testing frameworks :/
                self.__getattribute__(public_name)(*args, **kwargs)
            setattr(cls, special_method_name, wrapper)
        
        special_names = filter(lambda name: name.startswith('__') and name.endswith('__'), dir(cls))
        # Assumes that all public methods are matchers
        matcher_names = filter(lambda name: not name.startswith('_'), dir(cls))
        public_matcher_names_by_matcher = dict()
        for name in matcher_names:
            matcher = getattr(cls, name)
            public_matcher_names_by_matcher[matcher] = name
        matchers = list(public_matcher_names_by_matcher.keys())
        
        for special_name in special_names:
            matcher = getattr(cls, special_name)
            if matcher in matchers:
                public_name = public_matcher_names_by_matcher[matcher]
                wrap(special_name, public_name)
    

## Unit Tests ###########################################################################################

from unittest import TestCase, main
class ExpectTest(TestCase):
    
    # Meta functionality
    
    def test_can_subclass_expect(self):
        """Usefull if you want to extend expect with custom matchers without polluting the original expect()
        Used in the test suite to keep test isolation high."""
        class local_expect(expect): pass
        local_expect(1).equals(1)
        expect(lambda: local_expect(1).equals(2)).to_raise(AssertionError, r"^Expect 1 to equal 2$")
    
    def test_can_add_custom_matchers(self):
        calls = []
        class local_expect(expect): pass
        local_expect.custom_matcher = lambda *arguments: calls.append(arguments)
        
        instance = local_expect('foo')
        instance.custom_matcher()
        instance.custom_matcher('bar', 'baz')
        
        expect(calls).to.contain((instance,))
        expect(calls).to.contain((instance, 'bar', 'baz'))
    
    def test_assertion_error_from_matcher_is_enhanced(self):
        def raise_(self):
            raise AssertionError('sentinel')
        expect.fnord = raise_
        expect(lambda: expect(1).fnord()).raises(AssertionError, r"Expect 1 sentinel")
        expect(lambda: expect(1).not_fnord()).raises(AssertionError, r"Expect 1 not sentinel")
    
    def test_assertion_can_contain_unicode_message(self):
        class local_expect(expect): pass
        local_expect.fnord = lambda self: self._assert(False, "Fnörd")
        expect(lambda: local_expect(1).fnord()).to_raise(AssertionError, r"^Expect 1 Fnörd$")
        
        local_expect.fnord = lambda self: self._assert(False, u"Fnörd")
        expect(lambda: local_expect(1).fnord()).to_raise(AssertionError, r"^Expect 1 Fnörd$")
    
    def test_error_message_when_calling_non_existing_matcher_is_good(self):
        expect(lambda: expect('fnord').nonexisting_matcher()) \
            .to_raise(AssertionError, r"Tried to call non existing matcher 'nonexisting_matcher'")
    
    def test_not_is_only_allowed_on_word_boundaries(self):
        expect(lambda: expect(True).nothing_that_negates.is_(True)).not_.to_raise()
        expect(lambda: expect(True).annotation.to.be(True)).not_.to_raise()
        expect(lambda: expect(True).an_not_ation.to.be(True)).to_raise()
        expect(lambda: expect(True).an_not.to.be(True)).to_raise()
    
    def test_can_specify_custom_message(self):
        def messaging(message):
            return lambda: expect(True, message=message).not_.to_be(True)
        expect(messaging('fnord')).to_raise(AssertionError, r"^fnord$")
        expect(messaging('fnord <{assertion_message}> fnord')) \
            .to_raise(AssertionError, r"^fnord <Expect True not to be True> fnord$")
        expect(messaging('{expected}-{optional_negation}')).to_raise(AssertionError, r"^True- not $")
        expect(messaging('{expected}')).to_raise(AssertionError, r"^True$")
        
        expect(lambda: expect.with_message('fnord', True).to.be(False)) \
            .to_raise(AssertionError, r"^fnord$")
        
        # TODO: allow partially formatted messages from expect.with_message
    
    def test_can_return_error_instead_of_raising(self):
        # Idea: have a good api to check expectations without raising
        expect(expect(False, should_raise=False).to_be(False)).equals((True, ""))
        expect(expect(False, should_raise=False).not_to.be(True)).equals((True, ""))
        expect(expect.returning(False).to_be(False)).equals((True, ""))
        expect(expect.returning(False).to_be(True)).to_equal((False, "Expect False to be True"))
    
    def test_hides_double_underscore_alternative_names_from_tracebacks(self):
        assertion = None
        try:
            expect(3) != 3
        except AssertionError as a:
            assertion = a
        
        expect(assertion) != None
        import traceback
        traceback = '\n'.join(traceback.format_tb(sys.exc_info()[2]))
        expect(traceback).not_to.contain('_assert')
        # Would like this one too, but is only hidden in py.test
        # expect(traceback).not_to.contain('self(')
    
    def test_not_in_path_inverts_every_matcher(self):
        expect(3).to_be(3)
        expect(3).not_to_be(2)
        expect(lambda: expect(3).not_to_be(3)) \
            .to_raise(AssertionError, r"^Expect 3 not to be 3$")
        
        expect(lambda: None).not_to_raise(AssertionError)
        raising = lambda: expect(lambda: 1 / 0).not_to_raise(ZeroDivisionError)
        expect(raising).to_raise(AssertionError, "division.* by zero")
    
    def _test_missing_argument_to_expect_raises_with_good_error_message(self):
        pass
    
    def _test_stacktrace_contains_matcher_as_top_level_entry(self):
        pass
    
    def _test_stacktrace_does_not_contain_internal_methods(self):
        pass
    
    # Matchers ##########################################################################################
    
    # REFACT: rename tests to use the canonical name
    def test_trueish(self):
        expect(True).is_.trueish()
        expect(True).is_.truish()
        expect([1]).is_.trueish()
        expect(False).is_not.trueish()
        expect("1").is_.trueish()
        expect([]).is_not.trueish()
        expect("").is_not.trueish()
        
        expect(lambda: expect([]).to_be.trueish()) \
            .to_raise(AssertionError, r"Expect \[\] to be trueish")
        expect(lambda: expect([1]).not_to_be.trueish()) \
            .to_raise(AssertionError, r"Expect \[1\] not to be trueish")
    
    def test_falseish(self):
        expect(False).to.be.falsish()
        expect(False).to.be.falseish()
        expect(0).to.be.falseish()
        expect('').to.be.falseish()
        expect([]).to.be.falseish()
        expect(tuple()).to.be.falseish()
        expect('foo').not_to.be.falsish()
        
        expect(lambda: expect('foo').to.be.falsish()) \
            .to_raise(AssertionError, r"")
    
    def test_true(self):
        expect(True).true()
        expect(False).is_not.true()
        expect([1]).is_not.true()
        expect("1").is_not.true()
        
        expect(lambda: expect('fnord').to_be.true()) \
            .to_raise(AssertionError, r"Expect 'fnord' to be True")
        expect(lambda: expect(True).not_to_be.true()) \
            .to_raise(AssertionError, r"Expect True not to be True")
    
    def test_false(self):
        expect(False).to.be.false()
        expect(None).not_to_be.false()
        expect([]).not_to_be.false()
        expect("").not_to_be.false()
        expect(0).not_to_be.false()
        
        
        expect(lambda: expect('fnord').to.be.false()) \
            .to_raise(AssertionError, r"Expect 'fnord' to be False")
        expect(lambda: expect(0).to.be.false()) \
            .to_raise(AssertionError, r"Expect 0 to be False")
    
    def test_equal(self):
        expect('foo').equals('foo')
        expect('foo').to.equal('foo')
        expect('foo').not_to.equal('fnord')
        expect(23).equals(23)
        expect([]).equals([])
        expect(10) == 10
        expect(10) != 12
        
        expect(lambda: expect([]) == set()).to_raise(AssertionError, r"Expect \[\] to equal set")
        expect(lambda: expect(1) != 1).to_raise(AssertionError, r"Expect 1 not to equal 1")
        expect(lambda: expect(23).to.equal(42)) \
            .to_raise(AssertionError, r"Expect 23 to equal 42")
        expect(lambda: expect(23).not_to.equal(23)) \
            .to_raise(AssertionError, r"Expect 23 not to equal 23")
        
        # FIXME: make output multi line to make it easier to parse if individual output is longish
    
    def test_identical(self):
        expect(True).is_identical(True)
        expect(1).is_(1)
        expect(1).not_.to.be(2)
        marker = object()
        expect(marker).to.be(marker)
        
        expect(lambda: expect(1).to.be(2)) \
            .to_raise(AssertionError, r"Expect 1 to be 2")
        expect(lambda: expect(1).not_to.be(1)) \
            .to_raise(AssertionError, r"Expect 1 not to be 1")
    
    def test_none(self):
        expect(None).is_none()
        expect(0).is_not.none()
        expect(False).is_not.none()
        expect(lambda: expect(3).is_.none()).to_raise(AssertionError, r"Expect 3 to be None")
    
    def test_exists(self):
        expect(0).exists()
        expect([]).exists()
        expect(False).exists()
        expect(None).does_not.exist()
        
        expect(lambda: expect(None).exists()).to_raise(AssertionError, r"Expect None to exist")
    def test_included_in(self):
        expect(1).is_included_in(1,2,3)
        expect(1).is_included_in([1,2,3])
        expect(23).is_not.included_in(1,2,3)
        expect('fnord').is_included_in('foo fnord bar')
        expect('foo').in_(dict(foo='bar'))
        
        expect(lambda: expect(23).is_included_in(0,8,15)) \
            .to_raise(AssertionError, r"Expect 23 is included in \[0, 8, 15]")
        expect(lambda: expect(23).is_included_in([0,8,15])) \
            .to_raise(AssertionError, r"Expect 23 is included in \[0, 8, 15]")
    
    def test_includes(self):
        expect("abbracadabra").includes('cada')
        expect([1,2,3,4]).include(3)
        expect([23,42]).not_to.contain(7)
        expect(dict(foo='bar')).includes('foo')
        expect([1,2,3,4]).includes(2,3)
        expect(dict(foo='bar')).has_key('foo')
        
        expect(lambda: expect([1,2]).to.contain(3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
        expect(lambda: expect([1,2]).to_include(2,3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
        
        expect(lambda: expect((1,2)).includes()).to_raise(TypeError, r"includes\(\) takes at least 2 arguments \(1 given\)")
    
    def test_has_subdict(self):
        expect(dict()).to_have.subdict()
        expect(dict(foo='bar')).to.have.subdict()
        expect({'foo': 'bar'}).to.have_subdict({'foo': 'bar'})
        expect(dict(foo='bar')).to_have.subdict(foo='bar')
        expect(dict(foo='bar')).not_to.have.subdict(bar='bar')
        expect(dict(foo='bar')).not_to.have.subdict(foo='bar', bar='foo')
        
        # lists in keys
        expect(dict(foo=['bar'])).to.have_subdict(foo=['bar'])
        
        expect(lambda: expect(42).has_subdict())\
            .to_raise(AssertionError, r"Expect 42 to be instance of 'dict'")
        
        expect(lambda: expect(dict()).to_have.subdict(foo='bar')) \
            .to_raise(AssertionError, r"Expect {} to contain dict {'foo': 'bar'}")
        expect(lambda: expect(dict(foo='bar')).to_have.subdict(foo='baz')) \
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} to contain dict {'foo': 'baz'}")
        expect(lambda: expect(dict(foo='bar')).not_to_have.subdict(foo='bar')) \
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} not to contain dict {'foo': 'bar'}")
    
    def test_matching(self):
        expect("abbbababababaaaab").is_matching(r"[ab]+")
        expect("fnordabbafnord").matches(r"[ab]+")
        expect("cde").to_not.match(r"[ab]+")
        expect("fnord").matches(r"^fnord$")
        expect('bar').matches(r'\Abar\Z')
        expect('bär').matches(r'\Abär\Z')
        
        expect(lambda: expect(32).matches("32"))\
            .raises(AssertionError, r"Expect 32 to be instance of '.*str.*'")
        
        expect(lambda: expect('foo\nbar\nbaz').matches(r'^bar$')).to_raise(AssertionError)
        expect(lambda: expect('cde').matches(r'fnord')) \
            .to_raise(AssertionError, r"Expect 'cde' to be matched by regex r'fnord'")
    
    def test_raises(self):
        # is it an error to raise any other exception if a specific exception is expected? - yes
        # is it an error to raise any other exception if a specific exception is not expected? - could be ok, could be raised through
        
        class TestException(Exception): pass
        def raiser(): raise TestException('test_exception')
        
        # first argument should be callable
        expect(lambda: expect(42).to_raise()) \
            .to_raise(AssertionError, r"Expect 42 to be callable")
        expect(lambda: expect(42).not_.to_raise()) \
            .to_raise(AssertionError, r"Expect 42 to be callable")
        
        # simple positive
        expect(raiser).to_raise()
        expect(raiser).to_raise(TestException)
        expect(raiser).to_raise(TestException, r'test_[ent]xception') # regex
        
        # simple negative
        expect(lambda:None).not_to.raise_()
        expect(lambda:None).not_to.raise_(TestException)
        expect(lambda:None).not_to.raise_(TestException, 'fnord')
        
        # expected but not raising
        expect(lambda: expect(lambda:None).to_raise()) \
            .to_raise(AssertionError, r"> to raise Exception but it raised:\n\tNone")
        # raising unexpected
        expect(lambda: expect(raiser).not_to.raise_()) \
            .to_raise(AssertionError, r"> not to raise Exception but it raised:\n\tTestException\('test_exception',\)$")
        expect(lambda: expect(raiser).not_to.raise_(TestException)) \
            .to_raise(AssertionError, r"> not to raise TestException but it raised:\n\tTestException\('test_exception',\)$")
        expect(lambda: expect(raiser).not_to.raise_(TestException, r"^test_exception$")) \
            .to_raise(AssertionError, r"> not to raise TestException with message matching:\n\tr'\^test_exception\$'\nbut it raised:\n\tTestException\('test_exception',\)$")
            
        # raising right exception, wrong message
        expect(lambda: expect(raiser).to_raise(TestException, r'fnord')) \
            .to_raise(AssertionError, r"> to raise TestException with message matching:\n\tr'fnord'\nbut it raised:\n\tTestException\('test_exception',\)$")
        
        # negative raises different (swallowed)
        expect(lambda: expect(raiser).not_to.raise_(ArithmeticError)).not_.to_raise()
        # negative raise correct but wrong message (swallowed)
        expect(lambda: expect(raiser).not_to.raise_(TestException, r'fnord')).not_.to_raise()
        # negative raise wrong exception but right messagge (swallowed)
        expect(lambda: expect(raiser).not_to.raise_(ArithmeticError, r'test_exception')).not_.to_raise()
        # wrong exception, wrong message (swallowed)
        expect(lambda: expect(raiser).not_.to_raise(NameError, r'fnord')).not_.to_raise()
        
        # Can catch exceptions that do not inherit from Exception to ensure everything is testable
        expect(lambda: sys.exit('gotcha')).to_raise(SystemExit)
        
        # Return caught exception
        exception = expect(raiser).to_raise(TestException)
        expect(exception).is_instance_of(TestException)
        expect(str(exception)).matches('test_exception')
    
    def test_empty(self):
        expect("").is_empty()
        expect([]).is_empty()
        expect(tuple()).is_empty()
        expect(dict()).is_empty()
        
        expect("12").is_not.empty()
        expect([12]).is_not.empty()
        expect((12,23)).is_not.empty()
        expect(dict(foo='bar')).is_not.empty()
        
        expect(lambda: expect("23").is_empty()) \
            .to_raise(AssertionError, r"Expect '23' to be empty")
    
    def test_is_instance_of(self):
        expect(dict()).is_instance(dict)
        expect("").is_instance(str)
        
        expect(lambda: expect("").instanceof(list)).to_raise(AssertionError, r"Expect '' to be instance of 'list'")
    
    def test_is_callable(self):
        expect(lambda:None).is_callable()
        def foo():pass
        expect(foo).is_.callable()
        expect(3).is_not.callable()
        
        expect(lambda: expect(3).is_.callable()) \
            .raises(AssertionError, r"Expect 3 to be callable")
    
    def test_has_length(self):
        expect("123").has_length(3)
        expect(set([1])).len(1)
        
        expect(lambda: expect([42]).to_have.length(23)) \
            .to_raise(AssertionError, r"Expect \[42\] to have length 23, but found length 1")
    
    def test_greater_than(self):
        expect(3).is_greater_than(1)
        expect(3) > 1
        expect(lambda: expect(10) > 15).to_raise(AssertionError, r"Expect 10 to be greater than 15")
        expect(lambda: expect(1).is_greater_than(3)) \
            .to_raise(AssertionError, r"Expect 1 to be greater than 3")
    
    def test_greater_or_equal_than(self):
        expect(3).is_greater_or_equal_than(3)
        expect(3).is_greater_or_equal_than(2)
        expect(7) >= 7
        expect(5) >= 2
        
        expect(lambda: expect(20) >= 30).to_raise(AssertionError, r"Expect 20 to be greater or equal than 30")
    
    def test_less_than(self):
        expect(7).is_smaller_than(10)
        expect(10) < 12
        expect(lambda: expect(10) < 3).to_raise(AssertionError, "Expect 10 to be less than 3")
    
    def test_less_or_equal_than(self):
        expect(10).is_smaller_or_equal_than(10)
        expect(10) <= 10
        expect(lambda: expect(10) <= 5).raises(AssertionError, "Expect 10 to be less or equal than 5")
    
    def test_between(self):
        expect(3).is_between(1,10)
        expect(lambda: expect(10).is_between(1,3)).to_raise(AssertionError, "Expect 10 to be between 1 and 3")
    

    def test_close_to(self):
        expect(3.4).is_close_to(3, 0.5)
        expect(-3.4).is_close_to(-3, 0.5)
        expect(3.4).is_close_to(3.1, 0.5)
        expect(3.4).is_close_to(10, 10)
        expect(10.2).not_to_be.close_to(3, 4)
        expect(-3).is_not.close_to(-2, 0.5)
        
        expect(lambda: expect(10).is_.close_to(2, 3)).to_raise(AssertionError, "Expect 10 to be close to 2 with max delta 3")
    
    def _test_increases_by(sel):
        # Not sure what the right syntax for this should be
        # increase_by, increases_by
        # with expect(count_getter).increases_by(a_number):
        #   increase_count()
        # expect(increaser).to.increase_by(accessor, a_number)
        # expect(increaser, accessor).increases_by(a_number)
        pass
    

if __name__ == '__main__':
    main()
