#!/usr/bin/env python
# encoding: utf8

# BSD Licensed <http://opensource.org/licenses/BSD-2-Clause>
# Author: Martin Häcker mhaecker ät mac dot com

__all__ = ['expect', 'returning_expect']

import re

def returning_expect(expected):
    """Convenience method for a non raising expect().
    
    Works like a regular expect(), but instead of raising AssertionError it returns
    a (boolean, string) tupple that contains the expectation result and either the empty string
    or the Expectation message that would have been on the AssertionError.
    
    To get a callable reuseable expectation, use it like this:
    
        an_expectation = lambda expected: returning_expect(expected).to_be('fnord')
    """
    return expect(expected, should_raise=False)

class expect(object):
    """Minimal implementation of the expect pattern.
    
    The whole point of the expect patter is to allow concise assertions 
    that generate predictable and good error messages.
    
    This is best explained in cotrast to the classic assertion pattern like the python
    unittest module uses. For example:
    
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
    
    If you want to add custom matchers, just add them as instance methods to the expect object.
    """
    
    def __init__(self, expected, should_raise=True):
        self._expected = expected
        self._should_raise = should_raise
        self._expected_assertion_result = True
        self._selected_matcher = None
        self._selected_matcher_name = None
    
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
        Provides a good error message if you mistype"""
        # Integration with py.test - this hides the __call__ method from the generated traceback
        __tracebackhide__ = True
        
        if self._selected_matcher is None:
            raise AssertionError("Tried to call non existing matcher '{}'".format(self._selected_matcher_name))
        
        # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
        # Hides the actual matcher and all the methods it calls to assert stuff.
        try:
            self._selected_matcher(*args, **kwargs)
        except AssertionError, assertion:
            if self._should_raise:
                raise assertion # hide internal expect() methods from backtrace
            
            # Support returning_expect
            return (False, assertion.message)
        
        return (True, "")
    
    def _assert(self, assertion, message_format, *message_positionals, **message_keywords):
        def message():
            negation = ' not ' if self._expected_assertion_result is False else ' '
            return "Expect {!r}".format(self._expected) \
                + negation \
                + message_format.format(*message_positionals, **message_keywords)
        
        assert assertion is self._expected_assertion_result, message()
    
    def _assert_if_positive(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._expected_assertion_result is False:
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _assert_if_negative(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._expected_assertion_result is True:
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    ## Matchers #########################################################################################
    # REFACT: find a naming rule that fits all matchers. Should be clear, short, active, ...
    
    def is_true(self):
        self._assert(self._expected is True, "to be True")
    true = is_true
    
    def is_false(self):
        self._assert(self._expected is False, "to be False")
    false = is_false
    
    def is_equal(self, something):
        self._assert(something == self._expected, "to be equal to {}", something)
    
    equals = equal = to_equal = is_equal
    
    def to_be(self, something):
        self._assert(something is self._expected, "to be {}", something)
    
    is_ = be = is_same = is_identical = to_be
    
    def is_trueish(self):
        self._assert(bool(self._expected) is True, "to be trueish")
    truish = trueish = is_trueish
    
    def is_falseish(self):
        self._assert(bool(self._expected) is False, "to be falseish")
    falsish = falseish = is_falseish
    
    def is_included_in(self, sequence_or_atom, *additional_atoms):
        sequence = sequence_or_atom
        if len(additional_atoms) > 0:
            sequence = [sequence_or_atom]
            sequence.extend(additional_atoms)
        
        self._assert(self._expected in sequence, "is included in {}", sequence)
    in_ = included_in = is_included_in
    
    def does_include(self, something):
        self._assert(something in self._expected, "to include {}", something)
    contain = contains = include = includes = does_include
    
    def has_subdict(self, **a_subdict):
        for key, value in a_subdict.iteritems():
            self._assert_if_positive(key in self._expected, 'to have key "{}"', key)
            
            if key in self._expected:
                self._assert(value == self._expected[key], "to have value of {} equal {}", key, value)
    
    subdict = has_subdict
    
    def to_match(self, regex):
        import re
        self._assert(re.search(regex, self._expected) is not None, "to be matched by regex r'{}'", regex)
    match = matches = is_matching = to_match
    
    def to_raise(self, exception_class=Exception, message_regex=None):
        assert callable(self._expected), "Expect {!r} to be callable".format(self._expected)
        
        caught_exception = None
        try: self._expected()
        # We want to catch anything here to allow testing even for stuff like SystemExit
        except BaseException, exception: caught_exception = exception
        
        self._assert(isinstance(caught_exception, exception_class), "to raise {} but it raised {!r}", exception_class.__name__, caught_exception)
        if message_regex is not None:
            self._assert(re.search(message_regex, str(caught_exception)) is not None, "to raise {} with message matching r'{}' but it raised {!r}", exception_class.__name__, message_regex, caught_exception)
    throws = is_throwing = raise_ = raises = is_raising = to_raise

from unittest import TestCase, main
class ExpectTest(TestCase):
    
    def test_good_error_message_when_calling_non_existing_matcher(self):
        self.assertRaisesRegexp(AssertionError, r"Tried to call non existing matcher 'nonexisting_matcher'",
            lambda: expect('fnord').nonexisting_matcher())
    
    def test_should_ensure_not_is_on_word_boundaries(self):
        expect(lambda: expect(True).nothing.to_be(True)).not_.to_raise()
        expect(lambda: expect(True).annotation.to_be(True)).not_.to_raise()
        expect(lambda: expect(True).an_not_ation.to_be(True)).to_raise()
        expect(lambda: expect(True).an_not.to_be(True)).to_raise()
    
    def test_should_allow_custom_messages(self):
        # expect(key).is_(self._expected, message=Message('{} foo {}', foo, bar))
        self.fail()
    
    def test_should_allow_to_formulate_abstract_expectations(self):
        # Idea: have a good api to check expectations without raising
        expect(expect(False, should_raise=False).to_be(False)).equals((True, ""))
        expect(expect(False, should_raise=False).not_to.be(True)).equals((True, ""))
        expect(returning_expect(False).to_be(False)).equals((True, ""))
        expect(returning_expect(False).to_be(True)).to_equal((False, "Expect False to be True"))
    
    def test_can_add_custom_matchers(self):
        calls = []
        expect.custom_matcher = lambda self, *arguments: calls.append((self, arguments))
        
        instance = expect('foo')
        instance.custom_matcher()
        instance.custom_matcher('bar', 'baz')
        
        expect(calls).to.contain((instance, tuple()))
        expect(calls).to.contain((instance, ('bar', 'baz')))
    
    def test_has_subdict(self):
        expect(dict()).to_have.subdict()
        expect(dict(foo='bar')).to.have.subdict()
        expect(dict(foo='bar')).to_have.subdict(foo='bar')
        expect(dict(foo='bar')).not_to.have.subdict(bar='bar')
        
        self.fail('first differing key makes it not a subdict')
        
        expect(lambda: expect(dict()).to_have.subdict(foo='bar'))\
            .to_raise(AssertionError, r'Expect {} to have key "foo"')
        expect(lambda: expect(dict(foo='bar')).to_have.subdict(foo='baz'))\
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} to have value of foo equal baz")
        expect(lambda: expect(dict(foo='bar')).not_to_have.subdict(foo='bar'))\
            .to_raise(AssertionError, r"Expect {'foo': 'bar'} not to have value of foo equal bar")
    
    def test_is_equal(self):
        expect('foo').equals('foo')
        expect('foo').to.equal('foo')
        expect('foo').not_to.equal('fnord')
        expect(23).equals(23)
        expect([]).equals([])
        marker = object()
        expect(marker).to.be(marker)
        
        expect(lambda: expect(23).to.equal(42))\
            .to_raise(AssertionError, r"Expect 23 to be equal to 42")
        expect(lambda: expect(23).not_to.equal(23))\
            .to_raise(AssertionError, r"Expect 23 not to be equal to 23")
    
    def test_is_trueish(self):
        expect(True).is_.trueish()
        expect(True).is_.truish()
        expect([1]).is_.trueish()
        expect(False).is_not.trueish()
        expect("1").is_.trueish()
        expect([]).is_not.trueish()
        expect("").is_not.trueish()
        
        expect(lambda: expect([]).to_be.trueish())\
            .to_raise(AssertionError, r"Expect \[\] to be trueish")
        expect(lambda: expect([1]).not_to_be.trueish())\
            .to_raise(AssertionError, r"Expect \[1\] not to be trueish")
    
    def test_is_falseish(self):
        expect(False).to.be.falsish()
        expect(False).to.be.falseish()
        expect(0).to.be.falseish()
        expect('').to.be.falseish()
        expect([]).to.be.falseish()
        expect(tuple()).to.be.falseish()
        expect('foo').not_to.be.falsish()
        
        expect(lambda: expect('foo').to.be.falsish())\
            .to_raise(AssertionError, r"")
    
    def test_is_true(self):
        expect(True).true()
        expect(False).is_not.true()
        expect([1]).is_not.true()
        expect("1").is_not.true()
        
        expect(lambda: expect('fnord').to_be.true())\
            .to_raise(AssertionError, r"Expect 'fnord' to be True")
        expect(lambda: expect(True).not_to_be.true())\
            .to_raise(AssertionError, r"Expect True not to be True")
    
    def test_is_false(self):
        expect(False).to.be.false()
        expect(None).not_to_be.false()
        expect([]).not_to_be.false()
        expect("").not_to_be.false()
        expect(0).not_to_be.false()
        
        
        expect(lambda: expect('fnord').to.be.false())\
            .to_raise(AssertionError, r"Expect 'fnord' to be False")
        expect(lambda: expect(0).to.be.false())\
            .to_raise(AssertionError, r"Expect 0 to be False")
    
    def test_is_identical(self):
        expect(True).is_identical(True)
        expect(1).is_(1)
        expect(1).not_.to.be(2)
        
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
    
    def test_is_matching(self):
        expect("abbbababababaaaab").is_matching(r"[ab]+")
        expect("fnordabbafnord").matches(r"[ab]+")
        expect("cde").to_not.match(r"[ab]+")
        expect("fnord").matches(r"^fnord$")
        expect('bar').matches(r'\Abar\Z')
        
        expect(lambda: expect('foo\nbar\nbaz').matches(r'^bar$')).to_raise(AssertionError)
        expect(lambda: expect('cde').matches(r'fnord')) \
            .to_raise(AssertionError, r"Expect 'cde' to be matched by regex r'fnord'")
    
    def test_includes(self):
        expect("abbracadabra").includes('cada')
        expect([1,2,3,4]).include(3)
        expect([23,42]).not_to.contain(7)
        
        expect(lambda: expect([1,2]).to.contain(3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
    
    def test_is_raising(self):
        def raiser(): raise AssertionError('fnord')
        expect(raiser).to_raise()
        expect(raiser).to_raise(AssertionError)
        expect(raiser).not_to.raise_(ArithmeticError)
        expect(lambda:None).not_to.raise_()
        expect(lambda:None).not_to.raise_(AssertionError)
        expect(raiser).to_raise(AssertionError, r'fno[rl]d')
        expect(raiser).not_to.raise_(AssertionError, r'foobar')
        
        expect(lambda: expect(42).to_raise()) \
            .to_raise(AssertionError, r"Expect 42 to be callable")
        expect(lambda: expect(42).not_.to_raise()) \
            .to_raise(AssertionError, r"Expect 42 to be callable")
        
        expect(lambda: expect(raiser).not_to.raise_()) \
            .to_raise(AssertionError, r"Expect <function raiser .*> not to raise Exception but it raised AssertionError\('fnord',\)")
        expect(lambda: expect(raiser).not_to.raise_(AssertionError)) \
            .to_raise(AssertionError, r"Expect <function raiser .*> not to raise AssertionError")
        expect(lambda: expect(raiser).to_raise(AssertionError, r'fnold')) \
            .to_raise(AssertionError, r"Expect <function raiser .*> to raise AssertionError with message matching r'fnold'")
    

if __name__ == '__main__':
    main()