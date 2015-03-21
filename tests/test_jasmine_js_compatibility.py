from unittest import TestCase
from pyexpect import expect
from pyexpect.jasmine_js_compatibility import add_jasmine_js_matchers

class expect(expect):
    pass
add_jasmine_js_matchers(expect)

class JasmineMatcherNameCompatibilityTest(TestCase):

    # Jasmine compatibility
    # See: https://github.com/pivotal/jasmine/
    
    def test_can_activate_jasmine_compatibility(self):
        # see http://jasmine.github.io/edge/introduction.html for matcher examples
        a = object()
        expect(a).to_be(a)
        expect("foo").not_.to_be(None)
        expect(object()).not_.to_be(object())
        
        expect(12).to_equal(12)
        expect(dict(a=12, b=34)).to_equal(dict(a=12, b=34))
        
        message = "foo bar baz"
        expect(message).to_match(r"bar")
        expect(message).to_match("bar")
        expect(message).not_.to_match(r"quux")
        
        # not really equivalent, as python throws if you access undefined attributes
        defined = "defined"
        expect(defined).to_be_defined()
        
        # same problem
        expect(defined).not_.to_be_undefined()
        expect(None).to_be_undefined()
        
        expect(None).to_be_null()
        
        expect("foo").to_be_truthy()
        expect(dict()).not_.to_be_truthy()
        expect(None).to_be_falsy()
        expect([]).to_be_falsy()
        expect("").to_be_falsy()
        expect(tuple()).to_be_falsy()
        expect("foo").not_.to_be_falsy()
        
        array = ["foo", "bar", "baz"]
        expect(array).to_contain("bar")
        expect(array).not_.to_contain("quux")
        
        from math import e, pi
        expect(e).to_be_less_than(pi)
        expect(pi).not_.to_be_less_than(e)
        expect(pi).to_be_greater_than(e)
        expect(e).not_.to_be_greater_than(pi)
        
        # to_be_close_to differs from close_to in py_expect as it wants a precision argument
        # that specifies how many digits in the number should be identical. 
        # I find this highly annoying, as was not at all easy to use and quite hard to 
        # read and reason about after the fact. Especially as floats / doubles can have 
        # surprising internal representations.
        # Solution: Support the API but not by default. By default, the second parameter 
        # is assumed to be a max_delta which is much easier to reason about.
        expect(0).to_be_close_to(0)
        expect(1).to_be_close_to(0.5, 0.6)
        
        # precision argument (by default ignored)
        # round expected to n digits after the comma and then compare
        expect(pi).not_.to_be_close_to(e, precision=2)
        # expect(pi).to_be_close_to(e, 0)
        expect(pi).not_.to_be_close_to(e, precision=1)
        
        expect(1).to_be_close_to(1.001, precision=2)
        expect(2).not_.to_be_close_to(2.01, precision=2)
        expect(0).to_be_close_to(0.1, precision=0)
        expect(3).to_be_close_to(3.1, precision=0)
        expect(1).to_be_close_to(1.0001, precision=3)
        expect(1.23).to_be_close_to(1.229, precision=2)
        expect(1.23).to_be_close_to(1.226, precision=2)
        expect(1.23).to_be_close_to(1.225, precision=2)
        expect(1.23).not_.to_be_close_to(1.2249999, precision=2)
        expect(1.23).to_be_close_to(1.234, precision=2)
        
        def throws(): raise ArithmeticError()
        expect(throws).to_throw()
        expect(lambda: 3).not_.to_throw()
        