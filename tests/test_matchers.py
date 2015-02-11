# encoding: utf8

from unittest import TestCase
import sys

from pyexpect import expect

class MatcherTest(TestCase):
    
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
            .to_raise(AssertionError, r"Expect 23 is included in \(0, 8, 15\)")
        expect(lambda: expect(23).is_included_in([0,8,15])) \
            .to_raise(AssertionError, r"Expect 23 is included in \[0, 8, 15\]")
    
    def test_includes(self):
        expect("abbracadabra").includes('cada')
        expect([1,2,3,4]).include(3)
        expect([23,42]).not_to.contain(7)
        expect(dict(foo='bar')).includes('foo')
        expect([1,2,3,4]).includes(2,3)
        expect(dict(foo='bar')).has_key('foo')
        
        expect(lambda: expect([1,2]).to.contain(3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
        expect(lambda: expect([1,2]).to_include(2,3)).to_raise(AssertionError, r"Expect \[1, 2] to include 3")
        
        native_python_error_message = r"includes\(\) missing 1 required positional argument: 'needle'"
        if sys.version < '3':
            native_python_error_message = r"includes\(\) takes at least 2 arguments \(1 given\)"
        
        expect(lambda: expect((1,2)).includes()).to_raise(TypeError, native_python_error_message)
    
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
        expect("").is_instance(str, object)
        
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
        # TODO: should assert that out supports __len__
    
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
    
    def test_hasattr(self):
        expect(dict()).hasattr('items')
        expect(object).not_.hasattr('fnord')
        
        expect(lambda: expect(object).hasattr('fnord')).to_raise(AssertionError, "Expect <(?:class|type) 'object'> to have attribute 'fnord'")
    
    def test_is_subclass_of(self):
        expect(dict).is_subclass_of(object)
        expect(list).is_subclass_of(object, object)
        expect(dict).is_not.subclass_of(int)
        expect(lambda: expect(dict).subclass_of(int)).to_raise(AssertionError, "Expect <(?:class|type) 'dict'> to be subclass of <(?:class|type) 'int'>")
    
    def _test_increases_by(sel):
        # Not sure what the right syntax for this should be
        # increase_by, increases_by
        # with expect(count_getter).increases_by(a_number):
        #   increase_count()
        # expect(increaser).to.increase_by(accessor, a_number)
        # expect(increaser, accessor).increases_by(a_number)
        pass
    
    def test_starts_with(self):
        expect('fnordfoo').starts_with('fnord')
        # expect(['foo', 'bar']).starts_with('foo')
        expect(lambda: expect('fnord').starts_with('bar')).to_raise(
            AssertionError, "Expect 'fnord' to start with 'bar'"
        )
    
    def test_ends_with(self):
        expect('fnordfoo').ends_with('foo')
        # expect(['foo', 'bar']).ends_with('foo')
        expect(lambda: expect('fnord').ends_with('bar')).to_raise(
            AssertionError, "Expect 'fnord' to end with 'bar'"
        )
    
    def test_has_key(self):
        pass
    
    def test_has_subset(self):
        pass
