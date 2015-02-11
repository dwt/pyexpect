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
# - Improve py3 support - shorten exception stack traces
# - allow subexpects, i.e. matchers that are implemented in terms of other matchers
# - allow adding negation as a parameter to expect

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
        
        self._enable_nicer_backtraces_for_new_double_underscore_matcher_alternatives()
    
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
    
    ## Compatibility with other expectation packages ####################################################
    
    @classmethod
    def enable_jasmine_compatibility(cls):
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
        self._assert(self._actual is True, "to be True")
    
    is_true = true
    
    def false(self):
        self._assert(self._actual is False, "to be False")
    
    is_false = false
    
    def none(self):
        self._assert(self._actual is None, "to be None")
    
    is_none = none
    
    def exist(self):
        self._assert(self._actual is not None, "to exist (not be None)")
    
    exists = exist
    # REFACT: consider adding 'from' alias to allow syntax like expect(False).from(some_longish_expression())
    # Could enhance readability, not sure it's a good idea?
    def equal(self, something):
        self._assert(something == self._actual, "to equal {0!r}", something)
    
    __eq__ = equals = equal
    to_equal = is_equal = equal
    
    def different(self, something):
        self.not_ == something
    
    __ne__ = different
    is_different = different
    
    def be(self, something):
        self._assert(something is self._actual, "to be {0!r}", something)
    
    same = identical = is_ = be
    be_same = is_same = be_identical = is_identical = to_be = be
    
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
    
    # REFACT: Error message is hard to read., needs formatting on multiple lines, or restriction to just the keys in question.
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
    have_subdict = have_sub_dict = has_subdict = has_sub_dict = sub_dict
    
    def has_attribute(self, *attribute_names):
        for attribute_name in attribute_names:
            self._assert(hasattr(self._actual, attribute_name) is True, "to have attribute {0!r}", attribute_name)
    hasattr = has_attr = has_attribute
    have_attribute = have_attr = has_attribute
    
    def to_match(self, regex):
        string_type = str if sys.version > '3' else basestring
        expect(self._actual).is_instance(string_type)
        
        self._assert(re.search(regex, self._actual) is not None, "to be matched by regex r{0!r}", regex)
    
    match = matching = matches = to_match
    is_matching = to_match
    
    def to_start_with(self, expected_start):
        self._assert(self._actual.startswith(expected_start), "to start with {0!r}", expected_start)
    starts_with = startswith = to_start_with
    
    def to_end_with(self, expected_end):
        self._assert(self._actual.endswith(expected_end), "to end with {0!r}", expected_end)
    ends_with = endswith = to_end_with
    
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
        expect(self._actual).is_callable()
        
        caught_exception = None
        try:
            self._actual()
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
    is_raising = is_throwing = to_throw = to_raise
    
    def empty(self):
        self._assert(len(self._actual) == 0, "to be empty")
    
    is_empty = empty
    
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
    have_length = has_count = has_length = length
    
    def greater_than(self, smaller):
        self._assert(self._actual > smaller, "to be greater than {0!r}", smaller)
    
    __gt__ = bigger = larger = larger_than = greater = greater_than
    is_greater_than = is_greater = greater_than
    # TODO: consider to include *_then because it's such a common error?
    
    def greater_or_equal(self, smaller_or_equal):
        self._assert(self._actual >= smaller_or_equal, "to be greater or equal than {0!r}", smaller_or_equal)
    
    __ge__ = greater_or_equal_than = greater_or_equal
    is_greater_or_equal_than = is_greater_or_equal = greater_or_equal
    # TODO: consider to include *_then because it's such a common error?
    
    def less_than(self, greater):
        self._assert(self._actual < greater, "to be less than {0!r}", greater)
    
    __lt__ = smaller = smaller_than = lesser = lesser_than = less = less_than
    is_smaller_than = is_less_than = less_than
    # TODO: consider to include *_then because it's such a common error?
    
    def less_or_equal(self, greater_or_equal):
        self._assert(self._actual <= greater_or_equal, "to be less or equal than {0!r}", greater_or_equal)
    
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
        self._assert(lower <= self._actual <= higher, "to be between {0!r} and {1!r}", lower, higher)
    
    within_range = between
    is_within_range = is_between = between
    
    def close_to(self, expected, max_delta):
        self._assert((expected - max_delta) <= self._actual <= (expected + max_delta), "to be close to {0!r} with max delta {1!r}", expected, max_delta)
    
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
                raise AssertionError(message)
                # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
                # Hides the actual matcher and all the methods it calls to assert stuff.
            
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
        actual = self._actual
        optional_negation = ' not ' if self._is_negative() else ' '
        assertion_message = "Expect {actual!r}{optional_negation}{message}".format(**locals())
        
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
    
    def _concatenate(self, *args):
        return args
    
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
    


