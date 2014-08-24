# encoding: utf8

from unittest import TestCase
from pyexpect import expect

class MetaFunctionalityTest(TestCase):
    
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
    
    def test_not_negates_only_if_on_word_boundaries(self):
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
        expect(messaging('{actual}-{optional_negation}')).to_raise(AssertionError, r"^True- not $")
        expect(messaging('{actual}')).to_raise(AssertionError, r"^True$")
        
        expect(lambda: expect.with_message('fnord', True).to.be(False)) \
            .to_raise(AssertionError, r"^fnord$")
        
        # TODO: allow partially formatted messages from expect.with_message
        # Problem: the custom message is again piped through format, which breaks if 
        # the message contains user input
        # Probably needs two ways to hand in a message, one that is ok to format upon and one that is not
        # Consider api changes
        # expect.with_message('fnord')(3) == 3
        # expect(3).with_message('fnord') == 3
        # expect.with_message('fnord').that(3) == 3
        # expect(3).equals(3).with_message('fnord')
        # expect(3).equals(3, message='fnord')
        # expect(3, message='fnord', should_raise=False) == 3
        # expect(3, with_message='fnord') == 3
        # local_expect = expect.with_message('fnord')
        # local_expect(3) == 3
    
    def test_can_return_error_instead_of_raising(self):
        # Idea: have a good api to check expectations without raising
        expect(expect(False, should_raise=False).to_be(False)).equals((True, ""))
        expect(expect(False, should_raise=False).not_to.be(True)).equals((True, ""))
        expect(expect.returning(False).to_be(False)).equals((True, ""))
        expect(expect.returning(False).to_be(True)).to_equal((False, "Expect False to be True"))
    
    def test_not_in_path_inverts_every_matcher(self):
        expect(3).to_be(3)
        expect(3).not_to_be(2)
        expect(lambda: expect(3).not_to_be(3)) \
            .to_raise(AssertionError, r"^Expect 3 not to be 3$")
        
        expect(lambda: None).not_to_raise(AssertionError)
        raising = lambda: expect(lambda: 1 / 0).not_to_raise(ZeroDivisionError)
        expect(raising).to_raise(AssertionError, "division.* by zero")
    
    def test_missing_argument_to_expect_raises_with_good_error_message(self):
        expect(lambda: expect()).to_raise(TypeError)
    
    def _test_stacktrace_contains_matcher_as_top_level_entry(self):
        pass
    
    def _test_stacktrace_does_not_contain_internal_methods(self):
        pass
    
    def test_hides_double_underscore_alternative_names_from_tracebacks(self):
        import sys
        assertion = None
        try:
            expect(3) != 3
        except AssertionError as a:
            assertion = a
        
        expect(assertion) != None
        import traceback
        traceback = '\n'.join(traceback.format_tb(sys.exc_info()[2]))
        expect(traceback).not_to.contain('__ne__')
    
