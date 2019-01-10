# encoding: utf8

from pyexpect import expect
from unittest import TestCase
import sys

class MetaFunctionalityTest(TestCase):
    
    def test_can_subclass_expect(self):
        """Usefull if you want to extend expect with custom matchers without polluting the original expect()
        Used in the test suite to keep test isolation high."""
        class local_expect(expect):
            def local_matcher(self, arg):
                self._assert(self._actual == 1, "got " + arg)
        local_expect(1).local_matcher('one')
        expect(lambda: local_expect(2).local_matcher('two')).to_raise(AssertionError, r"^Expect 2 got two$")
    
    def test_can_add_custom_matchers_via_simple_assignment(self):
        calls = []
        class local_expect(expect): pass
        local_expect.custom_matcher = lambda *arguments: calls.append(arguments)
        
        instance = local_expect('foo')
        instance.custom_matcher()
        instance.custom_matcher('bar', 'baz')
        
        expect(calls).to.contain((instance,))
        expect(calls).to.contain((instance, 'bar', 'baz'))
    
    def test_error_message_is_sane(self):
        "Different ways to trigger the matchers should not generate the error message different"
        expect(lambda: expect(0) != 0).to_raise(AssertionError, "^Expect 0 not to equal 0$")
        expect(lambda: expect(0) == 1).to_raise(AssertionError, "^Expect 0 to equal 1$")
        
        expect(lambda: expect(0).is_.different(0)).to_raise(AssertionError, "^Expect 0 not to equal 0$")
        expect(lambda: expect(0).not_.equals(0)).to_raise(AssertionError, "^Expect 0 not to equal 0$")
        expect(lambda: expect(0).not_equals(0)).to_raise(AssertionError, "^Expect 0 not to equal 0$")
        expect(lambda: expect(0).equals(1)).to_raise(AssertionError, "^Expect 0 to equal 1$")
        
        # nested matcher
        expect(lambda: expect(0).to_raise()).to_raise(AssertionError, "^Expect 0 to be callable$")
    
    def test_wraps_really_long_error_messages_to_make_them_easier_to_read(self):
        error = expect(lambda: expect("really_long " * 50).to_equal('something shorter')).to_raise()
        expect(str(error)).to_match(r'\n\nto equal ')
    
    def test_assertion_can_contain_unicode_message(self):
        class local_expect(expect): pass
        local_expect.fnord = lambda self: self._assert(False, "Fnörd")
        expect(lambda: local_expect(1).fnord()).to_raise(AssertionError, r"^Expect 1 Fnörd$")
        
        local_expect.fnord = lambda self: self._assert(False, u"Fnörd")
        expect(lambda: local_expect(1).fnord()).to_raise(AssertionError, r"^Expect 1 Fnörd$")
    
    def test_error_message_when_calling_non_existing_matcher_is_good(self):
        expect(lambda: expect('fnord').nonexisting_matcher()) \
            .to_raise(NotImplementedError, r"Tried to call non existing matcher 'nonexisting_matcher'")
    
    def test_dont_double_enhance_exceptions_from_internally_used_expect_calls(self):
        class local_expect(expect):
            def nested_expect(self):
                expect(True, message='Fnord') == False
            def nested_assert(self):
                assert False, "Fnord"
        
        expect(lambda: local_expect(None).nested_expect()).to_raise(AssertionError, "^Fnord$")
        expect(lambda: local_expect(None).nested_assert()).to_raise(AssertionError, "^Fnord$")
    
    def test_can_specify_custom_message(self):
        def messaging(message):
            return lambda: expect(True, message=message).not_.to_be(True)
        expect(messaging('fnord')).to_raise(AssertionError, r"^fnord$")
        expect(messaging('fnord <{assertion_message}> fnord')) \
            .to_raise(AssertionError, r"^fnord <Expect True not to be True> fnord$")
        expect(messaging('{actual}-{optional_negation}')).to_raise(AssertionError, r"^True-not $")
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
        
        # Adding expect().with_message(...) and expect().should_raise(False) 
        # * could be done without breaking the api, but it would break the contract that all public methods are matchers.
        # * should_raise(False) is nicely symmetric, but it's a question whether the inverse .should_raise(True) is really 
        #   neccessary, as it is the default already? Maybe something shorter? expect().dont_raise().returning().raising().
    
    def test_not_negates_only_if_on_word_boundaries(self):
        expect(lambda: expect(True).nothing_that_negates.is_(True)).not_.to_raise()
        expect(lambda: expect(True).annotation.to.be(True)).not_.to_raise()
        expect(lambda: expect(True).an_not_ation.to.be(True)).to_raise()
        expect(lambda: expect(True).an_not.to.be(True)).to_raise()
    
    def test_not_in_path_inverts_every_matcher(self):
        expect(3).to_be(3)
        expect(3).not_to_be(2)
        expect(lambda: expect(3).not_to_be(3)) \
            .to_raise(AssertionError, r"^Expect 3 not to be 3$")
        
        expect(lambda: None).not_to_raise(AssertionError)
        raising = lambda: expect(lambda: 1 / 0).not_to_raise(ZeroDivisionError)
        expect(raising).to_raise(AssertionError, "division.* by zero")
    
    def test_not_in_path_finds_matchers_that_end_in_underscore_so_they_dont_collide_with_python_keywords(self):
        expect(3).not_in([1,2])
    
    def test_can_return_error_instead_of_raising(self):
        # Idea: have a good api to check expectations without raising
        expect(expect(False, should_raise=False).to_be(False)).equals((True, ""))
        expect(expect(False, should_raise=False).not_to.be(True)).equals((True, ""))
        expect(expect.returning(False).to_be(False)).equals((True, ""))
        expect(expect.returning(False).to_be(True)).to_equal((False, "Expect False to be True"))
    
    def test_missing_argument_to_expect_raises_with_good_error_message(self):
        expect(lambda: expect()).to_raise(TypeError)
    
    def test_should_not_add_extra_backtrace_if_causing_exception_in_python_3(self):
        if sys.version < '3':
            return # only a problem in python 3
        
        formatted = None
        try:
            expect(1).equals(2)
        except AssertionError as error:
            import traceback
            formatted = traceback.format_exc()
        
        expect(formatted).not_to_contain("During handling of the above exception, another exception occurred")
    
    def test_stacktrace_hides_most_of_the_internals_of_pyexpects_machinery(self):
        import traceback
        exception_traceback = None
        try:
            # Standard, should only contain __call__ as top level entry
            expect(1).equals(2)
        except AssertionError as error:
            _, _, exception_traceback = sys.exc_info()
        processed_traceback = traceback.extract_tb(exception_traceback)
        
        expect(processed_traceback).has_length(2)
        expect(processed_traceback[0]).to_contain('test_stacktrace_hides_most_of_the_internals_of_pyexpects_machinery')
        expect(processed_traceback[0]).to_contain('expect(1).equals(2)')
        
        expect(processed_traceback[1]).to_contain('pyexpect_internals_hidden_in_backtraces')
        expect(processed_traceback[1]).to_contain('raise exception # use `with expect.disabled_backtrace_cleaning():` to show full backtrace')
    
    def test_stacktrace_does_not_contain_an_extra_method_when_wrapping_operator_matchers(self):
        import traceback
        exception_traceback = None
        try:
            # Not the standard as it has more wrappers
            expect(1) == 2
        except AssertionError as error:
            _, _, exception_traceback = sys.exc_info()
        processed_traceback = traceback.extract_tb(exception_traceback)
        
        expect(processed_traceback).has_length(2)
        expect(processed_traceback[0]).to_contain('test_stacktrace_does_not_contain_an_extra_method_when_wrapping_operator_matchers')
        expect(processed_traceback[0]).to_contain('expect(1) == 2')
        
        expect(processed_traceback[1]).to_contain('pyexpect_internals_hidden_in_backtraces')
        expect(processed_traceback[1]).to_contain('raise exception # use `with expect.disabled_backtrace_cleaning():` to show full backtrace')
    
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
    
    def test_can_disable_backtrace_hiding(self):
        # To ease debugging matchers
        import traceback
        exception_traceback = None
        with expect.disabled_backtrace_cleaning():
            try:
                # Not the standard as it has more wrappers
                expect(1) == 2
            except AssertionError as error:
                _, _, exception_traceback = sys.exc_info()
        accessible_traceback = traceback.extract_tb(exception_traceback)
        # (filename, line number, function name, text)
        function_names = [function_name for _, _, function_name, _ in accessible_traceback]
        expect(function_names).contains('__call__')
        expect(function_names).contains('equal')
        expect(function_names).contains('_assert')
