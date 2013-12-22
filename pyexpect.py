#!/usr/bin/env python
# encoding: utf8

# BSD Licensed <http://opensource.org/licenses/BSD-2-Clause>
# Author: Martin Häcker mhaecker ät mac dot com

# Inspired by:
# Rubys RSpec that got me longing for a similar syntax
# Robert who suggested lots of great api ideas

__all__ = ['expect']

import re

class expect(object):
    """Minimal but very flexible implementation of the expect pattern.
    
    The whole point of the expect patter is to allow concise assertions 
    that generate predictable and good error messages.
    
    This is best explained in cotrast to the classic assertion pattern like the python
    unittest module uses. However, these assertions can be used anywhere and do not 
    depend on any unittest package. But now for the example:
    
        self.assertEquals('foo', 'bar)
    
    In this assertion it is not possible to see which of the arguments is the expected 
    and which is the actual value. While this ordering is mostly internally consistent 
    within the unittest package (sadly only mostly), it is not consistent between all 
    the different unit testing packages out there for python and especially not between
    different languages this pattern has been implemented on.
    
    To add insult to injury some frameworks will then output the error message like this:
    (Yes unittest I'm looking at you!)
    
        'bar' does not equal 'foo'
    
    It's easy to spend minutes till you remember or figure out that your framework 
    fooled you and inverted the order of arguments just to make it harder for you to 
    understand the code you are reading.
    
    If you are as annoyed by this as I am, allow me to introduce you to the expect pattern. 
    An assertion like this:
    
        expect('foo').to.equal('bar')
    
    Makes it absolutely plain what is the expected and what is the actual value. 
    No confusion possible. Also the error messages are designed to map cleanly back
    to the source code:
    
        Expect 'foo' to equal 'bar'.
    
    Thus the mapping from the error message is immediate and complete saving you minutes 
    each time, enhancing your focus, productivity and - most important - your enjoyment 
    when working with these expectations.
    
    Additionally they are not coupled to any TestCase class so you can easily reuse them 
    anywhere in your code to formalize expectations that your code has about some internal state.
    
    If you want to add custom matchers, just add them as instance methods to the expect object 
    like this:
    
        def my_matcher(self, arguments, defaults='something):
            pass # whatever you have to do. For helpers and availeable values see expect()
        expect.new_matcher = my_matcher
    """
    
    # TODO: Consider to add with statement support
    # with expect.raises(KeyError, 'fnord'):
    #     something_that_raises()
    
    def __init__(self, expected, should_raise=True, message=None):
        """Initialize a useable assertion object that you can chain off of.
        
        should_raise=False
            will toggle the behavior of the assertion to return a tuple
            (boolean, string) instead of raising an AssertionError or not raising
        
        message
            can be a custom message that replaces the original message in case of error.
            You can access the original message with the format `{assertion_message}` in 
            your message. For more details see the source of self._message()
        """
        self._expected = expected
        self._should_raise = should_raise
        self._custom_message = message
        self._expected_assertion_result = True
        self._selected_matcher = None
        self._selected_matcher_name = None
    
    @classmethod
    def with_message(cls, message, expected, **kwargs):
        """Convenience method to specify a custom message to expect()
        
        Works like the regular expect(), but instead of the error message from the matcher,
        the provided `message` will be used.
        
        You can access the original message with the format `{assertion_message}` in 
        your message. For more details see the source of self._message()
        """
        return cls(expected, message=message, **kwargs)
    
    @classmethod
    def returning(cls, expected, message=None, **kwargs):
        """Convenience method for a non raising expect()
        
        Works like a regular expect(), but instead of raising AssertionError it returns
        a (boolean, string) tupple that contains the expectation result and either the empty string
        or the Expectation message that would have been on the AssertionError.
        
        To get a callable reuseable expectation, use it like this:
        
            an_expectation = lambda expected: expect.returning(expected).to_be('fnord')
        """
        return cls(expected, should_raise=False, message=message, **kwargs)
    
    ## Internals ########################################################################################
    
    def _is_negative(self):
        return self._expected_assertion_result is False
    
    def __getattribute__(self, name):
        """Allows you to chain any python identifier to this object and keep 
        chaining for as long as you want as syntactic sugar.
        
        Only the last identifier that is then actually called has to be an actual 
        matcher.
        
        Including 'not' in any of the identifiers used in chaining will invert the 
        whole expectation.
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
        # REFACT: consider to support calling negated matchers directly with something like: expect(3).not_equals(2)
        if name.startswith('not_') or '_not_' in name or name.endswith('_not'):
            self._expected_assertion_result = False
        
        # If a matcher is availeable switch to it to allow calling it
        self._selected_matcher_name = name
        if hasattr(self.__class__, name):
            self._selected_matcher = object.__getattribute__(self, name)
        else:
            self._selected_matcher = None
        
        # Allow arbitrary chaining
        return self
    
    def __call__(self, *args, **kwargs):
        """Called whenever you actualy invoke a matcher. 
        
        Provides a good error message if you mistype the matcher name.
        
        Supports custom messages with the message keyword argument"""
        # Integration with py.test - this hides the __call__ method from the generated traceback
        __tracebackhide__ = True
        
        if self._selected_matcher is None:
            # REFACT: consider raising NotImplementedError
            raise AssertionError("Tried to call non existing matcher '{}' (Patches welcome!)".format(self._selected_matcher_name))
        
        # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
        # Hides the actual matcher and all the methods it calls to assert stuff.
        try:
            self._selected_matcher(*args, **kwargs)
        except AssertionError as assertion:
            if self._should_raise:
                raise assertion # hide internal expect() methods from backtrace
            
            # Support returning_expect
            return (False, str(assertion))
        
        return (True, "")
    
    # REFACT: would be nice if the name of this method makes it clear how the 
    # message should be worded to give a good error message
    def _message(self, message_format, *message_positionals, **message_keywords):
        expected = self._expected
        optional_negation = ' not ' if self._expected_assertion_result is False else ' '
        message = message_format.format(*message_positionals, **message_keywords)
        assertion_message = "Expect {expected!r}{optional_negation}{message}".format(
            expected=expected,
            optional_negation=optional_negation,
            message=message,
        )
        
        if self._custom_message is not None:
            return self._custom_message.format(**locals())
        
        return assertion_message
    
    def _assert(self, assertion, message_format, *message_positionals, **message_keywords):
        assert assertion is self._expected_assertion_result, \
            self._message(message_format, *message_positionals, **message_keywords)
    
    def _assert_if_positive(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._expected_assertion_result is False:
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _assert_if_negative(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._expected_assertion_result is True:
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    ## Matchers #########################################################################################
    
    # On naming matchers: Their name should be clear and fit in with the naming scheme of the existing 
    # matchers. That is: short, active, prepended with a conjugation of be
    # Sensible alternative names are encouraged after the method definition to allow the matchers
    # To be used sensibly in a sentence like matter for those who want it
    
    # On debugging matchers: Some pyton debuggers will hide all the internals of the expect method
    # To match py.tests behaviour. Read up on hidden frames and how to unhide them in your python debugger
    # `hf_unhide` is ofthen the keyword here.
    
    def is_true(self):
        self._assert(self._expected is True, "to be True")
    
    true = is_true
    
    def is_false(self):
        self._assert(self._expected is False, "to be False")
    
    false = is_false
    
    def is_equal(self, something):
        self._assert(something == self._expected, "to be equal to {}", something)
    
    __eq__ = equals = equal = to_equal = is_equal
    
    def __ne__(self, something):
        self.not_ == something
    
    def to_be(self, something):
        self._assert(something is self._expected, "to be {}", something)
    
    is_ = be = be_same = is_same = be_identical = is_identical = to_be
    
    def is_trueish(self):
        self._assert(bool(self._expected) is True, "to be trueish")
    
    truthy = truish = trueish = is_trueish
    
    def is_falseish(self):
        self._assert(bool(self._expected) is False, "to be falseish")
    
    falsy = falsish = falseish = is_falseish
    
    def does_include(self, something):
        self._assert(something in self._expected, "to include {}", something)
    
    contain = contains = include = includes = does_include
    
    def is_included_in(self, sequence_or_atom, *additional_atoms):
        sequence = sequence_or_atom
        if len(additional_atoms) > 0:
            sequence = [sequence_or_atom]
            sequence.extend(additional_atoms)
        
        self._assert(self._expected in sequence, "is included in {}", sequence)
    
    in_ = included_in = is_included_in
    
    def has_sub_dict(self, **a_subdict):
        assert isinstance(self._expected, dict), self._message("to be a dictionary", self._expected)
        
        subset = set(a_subdict.iteritems())
        superset = set(self._expected.iteritems())
        self._assert(len(subset - superset) == 0, 'to contain dict {}', a_subdict)
    
    includes_dict = contains_dict = sub_dict = subdict = has_subdict = has_sub_dict
    
    def to_match(self, regex):
        assert isinstance(self._expected, basestring), self._message("to be a string")
        
        self._assert(re.search(regex, self._expected) is not None, "to be matched by regex r'{}'", regex)
    
    match = matches = is_matching = to_match
    
    def to_raise(self, exception_class=Exception, message_regex=None):
        """Be carefull with negative raise assertions as they swallow all exceptions that you 
        don't specify. If you say `expect(raiser).not_.to_raise(FooException, 'fnord')` this 
        is interpreted as: every other exception that doesn't conform to this description is 
        ok and expected.
        """
        # REFACT: consider to change to_raise to let all unexpected exceptions pass through
        # Not sure what that means to correctly implement the negative side though
        assert callable(self._expected), "Expect {!r} to be callable".format(self._expected)
        
        # import sys; sys.stdout = sys.__stdout__; from bpdb import set_trace; set_trace()
        caught_exception = None
        try: self._expected()
        except BaseException as exception: caught_exception = exception
        
        is_right_class = isinstance(caught_exception, exception_class)
        if message_regex is None:
            self._assert(is_right_class, 
                "to raise {} but it raised:\n\t{!r}", exception_class.__name__, caught_exception)
        else:
            has_matching_message = re.search(message_regex, str(caught_exception)) is not None
            self._assert(is_right_class and has_matching_message, 
                "to raise {} with message matching:\n\tr'{}'\nbut it raised:\n\t{!r}", 
                exception_class.__name__, message_regex, caught_exception)
    
    throws = is_throwing = raise_ = raises = is_raising = to_raise
    
    def is_empty(self):
        self._assert(len(self._expected) == 0, "to be empty")
    
    empty = is_empty
    
    def is_instance(self, a_class):
        self._assert(isinstance(self._expected, a_class), "to be instance of '{}'", a_class.__name__)
    
    instanceof = instance_of = isinstance = is_instance
    
    def has_length(self, a_length):
        self._assert(len(self._expected) == a_length, "to have length {}", a_length)
    
    len = length = count = has_count = has_length
    
    def is_greater(self, smaller):
        self._assert(self._expected > smaller, "to be greater then {}", smaller)
    
    __gt__ = bigger = bigger_then = larger = larger_then = is_greater_then = is_greater
    
    def is_greater_or_equal(self, smaller_or_equal):
        self._assert(self._expected >= smaller_or_equal, "to be greater or equal then {}", smaller_or_equal)
    
    __ge__ = greater_or_equal_then = is_greater_or_equal_then = greater_or_equal = is_greater_or_equal
    
    def is_less_then(self, greater):
        self._assert(self._expected < greater, "to be less then {}", greater)
    
    __lt__ = smaller = smaller_then = lesser = lesser_then = less_then = smaller_then = is_smaller_then = is_less_then
    
    def is_less_or_equal(self, greater_or_equal):
        self._assert(self._expected <= greater_or_equal, "to be less or equal then {}", greater_or_equal)
    
    __le__ = smaller_or_equal = smaller_or_equal_then = is_smaller_or_equal = is_smaller_or_equal_then = is_less_or_equal_then = is_less_or_equal
    
    # REFACT: consider adding is_within_exclusive_range
    def is_within_range(self, lower, higher):
        self._assert(lower <= self._expected <= higher, "to be between {} and {}", lower, higher)
    
    is_between = is_within = is_within_range
    
    def is_close(self, actual, delta):
        self._assert((actual - delta) <= self._expected <= (actual + delta), "to be close to {} with max delta {}", actual, delta)
    
    almost_equal = is_almost_equal = close_to = is_close_to = is_close

from unittest import TestCase, main
class ExpectTest(TestCase):
    
    # Meta functionality
    
    def test_can_add_custom_matchers(self):
        calls = []
        expect.custom_matcher = lambda *arguments: calls.append(arguments)
        
        instance = expect('foo')
        instance.custom_matcher()
        instance.custom_matcher('bar', 'baz')
        
        expect(calls).to.contain((instance,))
        expect(calls).to.contain((instance, 'bar', 'baz'))
    
    def test_good_error_message_when_calling_non_existing_matcher(self):
        expect(lambda: expect('fnord').nonexisting_matcher()) \
            .to_raise(AssertionError, r"Tried to call non existing matcher 'nonexisting_matcher'")
    
    def test_should_ensure_not_is_on_word_boundaries(self):
        expect(lambda: expect(True).nothing.to_be(True)).not_.to_raise()
        expect(lambda: expect(True).annotation.to_be(True)).not_.to_raise()
        expect(lambda: expect(True).an_not_ation.to_be(True)).to_raise()
        expect(lambda: expect(True).an_not.to_be(True)).to_raise()
    
    def test_should_allow_custom_messages(self):
        def messaging(message):
            return lambda: expect(True, message=message).not_.to_be(True)
        expect(messaging('fnord')).to_raise(AssertionError, r"^fnord$")
        expect(messaging('fnord <{assertion_message}> fnord')) \
            .to_raise(AssertionError, r"^fnord <Expect True not to be True> fnord$")
        expect(messaging('{expected}-{optional_negation}')).to_raise(AssertionError, r"^True- not $")
        expect(messaging('{expected}')).to_raise(AssertionError, r"^True$")
        
        expect(lambda: expect.with_message('fnord', True).to.be(False)) \
            .to_raise(AssertionError, r"^fnord$")
    
    def test_should_allow_to_formulate_abstract_expectations(self):
        # Idea: have a good api to check expectations without raising
        expect(expect(False, should_raise=False).to_be(False)).equals((True, ""))
        expect(expect(False, should_raise=False).not_to.be(True)).equals((True, ""))
        expect(expect.returning(False).to_be(False)).equals((True, ""))
        expect(expect.returning(False).to_be(True)).to_equal((False, "Expect False to be True"))
    
    # Matchers
    
    def test_is_trueish(self):
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
    
    def test_is_falseish(self):
        expect(False).to.be.falsish()
        expect(False).to.be.falseish()
        expect(0).to.be.falseish()
        expect('').to.be.falseish()
        expect([]).to.be.falseish()
        expect(tuple()).to.be.falseish()
        expect('foo').not_to.be.falsish()
        
        expect(lambda: expect('foo').to.be.falsish()) \
            .to_raise(AssertionError, r"")
    
    def test_is_true(self):
        expect(True).true()
        expect(False).is_not.true()
        expect([1]).is_not.true()
        expect("1").is_not.true()
        
        expect(lambda: expect('fnord').to_be.true()) \
            .to_raise(AssertionError, r"Expect 'fnord' to be True")
        expect(lambda: expect(True).not_to_be.true()) \
            .to_raise(AssertionError, r"Expect True not to be True")
    
    def test_is_false(self):
        expect(False).to.be.false()
        expect(None).not_to_be.false()
        expect([]).not_to_be.false()
        expect("").not_to_be.false()
        expect(0).not_to_be.false()
        
        
        expect(lambda: expect('fnord').to.be.false()) \
            .to_raise(AssertionError, r"Expect 'fnord' to be False")
        expect(lambda: expect(0).to.be.false()) \
            .to_raise(AssertionError, r"Expect 0 to be False")
    
    def test_is_equal(self):
        expect('foo').equals('foo')
        expect('foo').to.equal('foo')
        expect('foo').not_to.equal('fnord')
        expect(23).equals(23)
        expect([]).equals([])
        expect(10) == 10
        expect(10) != 12
        
        expect(lambda: expect([]) == set()).to_raise(AssertionError, r"Expect \[\] to be equal to set\(\[\]\)")
        expect(lambda: expect(1) != 1).to_raise(AssertionError, r"Expect 1 not to be equal to 1")
        expect(lambda: expect(23).to.equal(42)) \
            .to_raise(AssertionError, r"Expect 23 to be equal to 42")
        expect(lambda: expect(23).not_to.equal(23)) \
            .to_raise(AssertionError, r"Expect 23 not to be equal to 23")
    
    def test_is_identical(self):
        expect(True).is_identical(True)
        expect(1).is_(1)
        expect(1).not_.to.be(2)
        marker = object()
        expect(marker).to.be(marker)
        
        expect(lambda: expect(1).to.be(2)) \
            .to_raise(AssertionError, r"Expect 1 to be 2")
        expect(lambda: expect(1).not_to.be(1)) \
            .to_raise(AssertionError, r"Expect 1 not to be 1")
    
    def test_is_included_in(self):
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
        
        expect(lambda: expect([1,2]).to.contain(3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
    
    def test_has_subdict(self):
        expect(dict()).to_have.subdict()
        expect(dict(foo='bar')).to.have.subdict()
        expect(dict(foo='bar')).to_have.subdict(foo='bar')
        expect(dict(foo='bar')).not_to.have.subdict(bar='bar')
        expect(dict(foo='bar')).not_to.have.subdict(foo='bar', bar='foo')
        
        expect(lambda: expect(42).has_subdict())\
            .to_raise(AssertionError, r"Expect 42 to be a dictionary")
        
        expect(lambda: expect(dict()).to_have.subdict(foo='bar')) \
            .to_raise(AssertionError, r"Expect {} to contain dict {'foo': 'bar'}")
        expect(lambda: expect(dict(foo='bar')).to_have.subdict(foo='baz')) \
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} to contain dict {'foo': 'baz'}")
        expect(lambda: expect(dict(foo='bar')).not_to_have.subdict(foo='bar')) \
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} not to contain dict {'foo': 'bar'}")
    
    def test_is_matching(self):
        expect("abbbababababaaaab").is_matching(r"[ab]+")
        expect("fnordabbafnord").matches(r"[ab]+")
        expect("cde").to_not.match(r"[ab]+")
        expect("fnord").matches(r"^fnord$")
        expect('bar').matches(r'\Abar\Z')
        
        expect(lambda: expect(32).matches("32"))\
            .raises(AssertionError, r"Expect 32 to be a string")
        
        expect(lambda: expect('foo\nbar\nbaz').matches(r'^bar$')).to_raise(AssertionError)
        expect(lambda: expect('cde').matches(r'fnord')) \
            .to_raise(AssertionError, r"Expect 'cde' to be matched by regex r'fnord'")
    
    def test_is_raising(self):
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
        import sys
        expect(lambda: sys.exit('gotcha')).to_raise(SystemExit)
    
    def test_is_empty(self):
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
    
    def test_is_instance(self):
        expect(dict()).is_instance(dict)
        expect("").is_instance(str)
        
        expect(lambda: expect("").instanceof(list)).to_raise(AssertionError, r"Expect '' to be instance of 'list'")
    
    def test_has_length(self):
        expect("123").has_length(3)
        expect(set([1])).len(1)
        
        expect(lambda: expect([1]).to_have.length(23)) \
            .to_raise(AssertionError, r"Expect \[1\] to have length 23")
    
    def test_is_greater_then(self):
        expect(3).is_greater_then(1)
        expect(3) > 1
        expect(lambda: expect(10) > 15).to_raise(AssertionError, r"Expect 10 to be greater then 15")
        expect(lambda: expect(1).is_greater_then(3)) \
            .to_raise(AssertionError, r"Expect 1 to be greater then 3")
    
    def test_is_greater_or_equal_then(self):
        expect(3).is_greater_or_equal_then(3)
        expect(3).is_greater_or_equal_then(2)
        expect(7) >= 7
        expect(5) >= 2
        
        expect(lambda: expect(20) >= 30).to_raise(AssertionError, r"Expect 20 to be greater or equal then 30")
    
    def test_is_less_then(self):
        expect(7).is_smaller_then(10)
        expect(10) < 12
        expect(lambda: expect(10) < 3).to_raise(AssertionError, "Expect 10 to be less then 3")
    
    def test_is_less_or_equal_then(self):
        expect(10).is_smaller_or_equal_then(10)
        expect(10) <= 10
        expect(lambda: expect(10) <= 5).raises(AssertionError, "Expect 10 to be less or equal then 5")
    
    def test_is_within_range(self):
        expect(3).is_within_range(1,10)
        expect(lambda: expect(10).is_within_range(1,3)).to_raise(AssertionError, "Expect 10 to be between 1 and 3")
    

    def test_is_close_to(self):
        expect(3.4).is_close_to(3, 0.5)
        expect(3.4).is_close_to(3.1, 0.5)
        expect(3.4).is_close_to(10, 10)
        expect(10.2).not_to_be.close_to(3, 4)
        
        expect(lambda: expect(10).is_.close_to(2, 3)).to_raise(AssertionError, "Expect 10 to be close to 2 with max delta 3")
    
if __name__ == '__main__':
    main()