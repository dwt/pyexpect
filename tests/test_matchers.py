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
    
    def test_has_sublist(self):
        expect([1,2,3,4]).has_sublist(2,3)
        expect([1,2,3,4]).has_sublist(2,3,4)
        expect([1,2,3,4]).has_sublist(1,2)
        expect([1,2,3,4]).has_sublist([1,2])
        expect((1,2,3,4)).has_sublist([1,2])
        expect([1,2,3,4]).has_sublist((1,2))
        expect("fnord").has_sublist("fnor")
        expect("fnord").has_sublist("nord")
        expect("fnord").not_has_sublist("fnordynator")

        expect(lambda: expect("foo").has_sublist('fnord')).to_raise(AssertionError,
            r"""Expect 'foo' to contain sequence 'fnord'""")
        expect(lambda: expect([1,2,3]).has_sublist(3,4)).to_raise(AssertionError,
            r"""Expect \[1, 2, 3] to contain sequence \(3, 4\)""")
    
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
        # In practice it's verry annoying if your test succeeds because you have a typo in the regex that checks the expectd message that you don't want to be raised -> so, raise it is
        
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
        expect(raiser).to_raise(TestException, r'test_[ent]xception') # regex support
        
        # simple negative
        expect(lambda:None).not_to.raise_()
        expect(lambda:None).not_to.raise_(TestException)
        expect(lambda:None).not_to.raise_(TestException, 'fnord')
        
        # expected but not raising
        expect(lambda: expect(lambda:None).to_raise()) \
            .to_raise(AssertionError, r">\s*to raise Exception but it raised:\s*None")
        # raising unexpected
        expect(lambda: expect(raiser).not_to.raise_()).to_raise(AssertionError,
            r">\s*not to raise Exception but it raised:\s*TestException\('test_exception',?\)$")
        expect(lambda: expect(raiser).not_to.raise_(TestException)).to_raise(AssertionError,
            r">\s*not to raise TestException but it raised:\n\tTestException\('test_exception',?\)$")
        expect(lambda: expect(raiser).not_to.raise_(TestException, r"^test_exception$")).to_raise(AssertionError,
            r">\s*not to raise TestException with message matching:\n\tr'\^test_exception\$'\nbut it raised:\n\tTestException\('test_exception',?\)$")
            
        # raising right exception, wrong message
        expect(lambda: expect(raiser).to_raise(TestException, r'fnord')).to_raise(AssertionError, 
            r">\s*to raise TestException with message matching:\n\tr'fnord'\nbut it raised:\n\tTestException\('test_exception',?\)$")
        
        # Can catch exceptions that do not inherit from Exception to ensure everything is testable
        expect(lambda: sys.exit('gotcha')).to_raise(SystemExit)
        
        # Returns caught exception
        exception = expect(raiser).to_raise(TestException)
        expect(exception).is_instance_of(TestException)
        expect(str(exception)).matches('test_exception')
    
    def test_raises_doesnt_swallow_exception_when_in_not_mode(self):
        class TestException(Exception): pass
        def raiser(): raise TestException('test_exception')
        
        # negative raises different
        expect(lambda: expect(raiser).not_to.raise_(ArithmeticError)).to_raise(TestException, r"test_exception")
        # negative raise correct but wrong message
        expect(lambda: expect(raiser).not_to.raise_(TestException, r'fnord')).to_raise(TestException, r"test_exception")
        # negative raise wrong exception but right messagge
        expect(lambda: expect(raiser).not_to.raise_(ArithmeticError, r'test_exception')).to_raise(TestException, r"test_exception")
        # wrong exception, wrong message
        expect(lambda: expect(raiser).not_.to_raise(NameError, r'fnord')).to_raise(TestException, r"test_exception")
        
        exception = backtrace = None
        try:
            expect(raiser).not_to.raise_(ArithmeticError)
        except TestException as e:
            exception = e
            _, _, backtrace = sys.exc_info()
        
        import traceback
        backtrace = traceback.extract_tb(backtrace)
        expect(backtrace[-1]).to_contain('raiser')
    
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
    
    def test_has_attributes_with_dict_param(self):
        class Foo(object):
            bar = 'baz'
            baz = 'quoox'
            
            def __repr__(self):
                return '<Foo bar=%r, baz=%r>' % (self.bar, self.baz)
            
        expect(Foo()).has_attributes(bar='baz', baz='quoox')
        # combines well with existing
        expect(Foo()).has_attributes('bar', 'baz', bar='baz', baz='quoox')
        # error cases
        expect(lambda: expect(Foo()).not_.to_have_attributes(fnord_attr='fnord_value')).not_.to_raise()
        expect(lambda: expect(Foo()).not_.to_have_attributes(baz='fnord_value')).not_.to_raise()
        
        expect(lambda: expect(Foo()).to_have_attributes(bar='quoox')) \
            .to_raise(AssertionError, "Expect <Foo bar='baz', baz='quoox'> to have attributes {'bar': 'quoox'}, \n\tbut has {'bar': 'baz'}")
        expect(lambda: expect(Foo()).not_.to_have_attributes(bar='fnord')) \
            .not_.to_raise(AssertionError, "Expect <Foo bar='baz', baz='quoox'> not to have attribute 'bar'")
    
    def test_is_subclass_of(self):
        expect(dict).is_subclass_of(object)
        expect(list).is_subclass_of(object, object)
        expect(dict).is_not.subclass_of(int)
        expect(lambda: expect(dict).subclass_of(int)).to_raise(AssertionError, "Expect <(?:class|type) 'dict'> to be subclass of <(?:class|type) 'int'>")
    
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
    
    
    def test_is_permutation_of(self):
        expect("fnord").is_permutation_of("fnord")
        expect("Martin").is_permutation_of("nitraM")
        expect("foo").is_permutation_of("ofo")
        expect([1,2,3]).is_permutation_of([3,2,1])
        
        expect(lambda: expect("foo").is_permutation_of("fnord")) \
            .to_raise(AssertionError, "^Expect 'foo' to be permutation of 'fnord'$")
        
        expect(lambda: expect(23).is_permutation_of("foo")) \
            .to_raise(TypeError, "'int' object is not iterable")
        
    
    def test_changes(self):
        # actor and getter need to be callable
        expect(lambda: expect('expected').to.change(lambda: None)) \
            .to_raise(AssertionError, "^Expect 'expected' to be callable$")
        expect(lambda: expect(lambda: None).to.change('getter')) \
            .to_raise(AssertionError, "^Expect 'getter' to be callable$")
        
        # numeric by argument
        expect(lambda: expect(id).to.change(id, by='by_fnord')) \
            .to_raise(AssertionError, "^Expect 'by_fnord' to be instance of 'Number'$")
        expect(lambda: expect(id).to.change(id, from_='from_fnord', by=2)) \
            .to_raise(AssertionError, "^Expect 'from_fnord' to be instance of 'Number'$")
        expect(lambda: expect(id).to.change(id, to='to_fnord', by=2)) \
            .to_raise(AssertionError, "^Expect 'to_fnord' to be instance of 'Number'$")
        
        # nothing specified - error
        expect(lambda: expect(id).to_change(id)).to_raise(AssertionError,
            "^At least one argument of 'from_', 'by', 'to' has to be specified$")
       
        # consistent arguments work
        state = dict(count=0)
        def actor(): state['count'] += 1
        def getter(): return state['count']
        def from_(from_=None, by=None, to=None):
            return lambda: expect(actor).to_change(getter, from_=from_, by=by, to=to)
        
        # inconsistent arguments
        assertion = expect(from_(0, by=1, to=2)) \
            .raises(AssertionError, r"^Inconsistant arguments: from=0 \+ by=1 != to=2$")
        expect(lambda: expect(id).to_change(id, from_=0, by=10, to=2)) \
            .to_raise(AssertionError, r"^Inconsistant arguments: from=0 \+ by=10 != to=2$")
        
        # fully specified
        expect(actor).to_change(getter, from_=0, by=1, to=1)
        
        # partially specified
        expect(actor).to_change(getter, from_=1, by=1)
        expect(actor).to_change(getter, from_=2, to=3)
        expect(actor).to_change(getter, from_=3)
        
        expect(actor).to_change(getter, by=1, to=5)
        expect(actor).to_change(getter, by=1)
        expect(actor).to_change(getter, to=7)
        
        # non numeric arguments
        def non_numeric(): return "something"
        expect(actor).to.change(non_numeric, from_="something")
        expect(actor).to.change(non_numeric, to="something")
        
        # None for from_ and to
        expect(actor).to_change(lambda: None, from_=None)
        expect(actor).to_change(lambda: None, to=None)
        
        # error messages
        expect(lambda: expect(actor).to.change(non_numeric, from_="nothing")) \
            .to_raise(AssertionError, "to start from 'nothing' but it changed from 'something' to 'something'$")
        expect(lambda: expect(actor).to.change(non_numeric, to="nothing")) \
            .to_raise(AssertionError, "to end with 'nothing' but it changed from 'something' to 'something'$")
        expect(lambda: expect(actor).to.change(non_numeric, by=2)) \
            .to_raise(AssertionError, "by=2 was given, but getter did not return a numeric value$")
        
        # only shows the first error when given multiple arguments
        # expect(lambda: expect(actor).to.change(non_numeric, from_="nothing")) \
        #     .to_raise(AssertionError, "to start from 'nothing' but it changed from 'something' to 'something'$")
        # expect(lambda: expect(actor).to.change(non_numeric, to="nothing")) \
        #     .to_raise(AssertionError, "to end with 'nothing' but it changed from 'something' to 'something'$")
        # expect(lambda: expect(actor).to.change(non_numeric, by=2)) \
        #     .to_raise(AssertionError, "to change by 2 but it changed from 'something' to 'something'$")
        
        # negations
        expect(actor).not_to_change(getter, from_=-1)
        expect(lambda: expect(actor).not_to_change(getter, from_=15)) \
            .to_raise(AssertionError, "not to start from 15 but it changed from 15 to 16$")
        expect(lambda: expect(actor).not_to_change(getter, to=17)) \
            .to_raise(AssertionError, "not to end with 17 but it changed from 16 to 17$")
        expect(lambda: expect(actor).not_to_change(getter, by=1)) \
            .to_raise(AssertionError, "not to change by 1 but it changed from 17 to 18$")
        
        # only shows the first problem in negation
        expect(lambda: expect(actor).not_to_change(getter, from_=18, by=1, to=19)) \
            .to_raise(AssertionError, "not to start from 18 but it changed from 18 to 19$")
        expect(lambda: expect(actor).not_to_change(getter, by=1, to=20)) \
            .to_raise(AssertionError, "not to change by 1 but it changed from 19 to 20$")
        expect(lambda: expect(actor).not_to_change(getter, to=21)) \
            .to_raise(AssertionError, "not to end with 21 but it changed from 20 to 21$")
        
        # accepts negations as soon as one of the constrained values diverges
        expect(actor).not_to_change(getter, from_=1, by=1, to=2)
        expect(actor).not_to_change(getter, from_=22, by=2, to=24)
        expect(actor).not_to_change(getter, by=2)
        expect(actor).not_to_change(getter, by=2, to=25)
        expect(actor).not_to_change(getter, from_=25, by=2)
        expect(actor).not_to_change(getter, from_=26, to=30)
        
        # TODO having multiple values to constrain the change with not can lead to unexpected passes
        # not quite sure what best to do about this, kind of similar to the problem with exceptions
        
        """
        Syntax ideas:
        
        expect(actor).to_change(getter, from_=about(3.3, max_delta=0.1), to=about(4.4, max_delta=0.1))
        about = expect.max_delta(0.1)
        expect(actor).to_change(getter, from_=about(3.3), to=about(4.4))
        expect(actor).to_change(getter, from_=expect.about(3.3, max_delta=0.1), to=expect.about(4.4,max_delta=0.1))
        expect(actor).to_change(getter, from_below=3.3, to_above=4.4)
        
        with expect(getter).changes(to=10):
            # actor code
        """
    
    def _test_increases_by(self):
        # decreases_by
        # Not sure what the right syntax for this should be
        # increase_by, increases_by
        # with expect(count_getter).increases_by(a_number):
        #   increase_count()
        # expect(increaser).to.increase_by(accessor, a_number)
        # expect(increaser, accessor).increases_by(a_number)
        pass
    
    
    def _test_in(self):
        expect('foo') in dict(foo='foo')
        expect(lambda: expect('foo') in dict(bar='bar')).to_raise(AssertionError)
    
    
    def _test_has_subset(self):
        pass
    
    def _test_time_tacking(self):
        pass
        """
        Idea is to allow easier measurement of expired seconds / time. Something along the lines of
        with expect.time_measurement as t:
            # something that takes some time
            expect(some_expected_time) == t.seconds()
            # or something similar
            """
