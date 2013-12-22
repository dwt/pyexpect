# pyexpect: Minimal but very flexible implementation of the expect pattern

The whole point of the expect patter is to allow concise assertions 
that generate predictable and good error messages.

Best viewed in an example:

    >>> expect(3).to_equal(4)
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "expect.py", line 146, in __call__
    AssertionError: Expect 3 to be equal to 4
    

Line noise is reduced as much as possible, so the error message is displayed as near to the problematic code as possible. No stack traces to dig through, clear and consistent error messages that tell you what went wrong. Thats how assertions should work.

## Why expect() over self.assert*

This is best explained in cotrast to the classic assertion pattern like the python
unittest module uses. However, these assertions can be used anywhere and do not 
depend on any unittest package. But now for the example:

    self.assertEquals('foo', 'bar')

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

## Why pyxpect over other python expect libraries

1.  Ease of use: Expect can be arbitrary chained with whatever you can think of (provided it's a valid python identifier):
    
        expect(23).to_be_chaned.with_something.that_makes_sense_in\
            .your_context.before_it.calls_the.matcher.equals(23)
    
    Matchers have many aliasses defined to enable you to write the expections in a natural way:
    
        expect(True).is_.true()
        expect(True).is_true()
        expect(True).is_equal(True)
        expect(True) == True
        expect(raising_calable).raises()
        expect(raising_calable).to_raises()
    
    Choose whatever makes sense for your specific test to read well so that reading the test later feels natural and transports the meaning of the code as best as possible.

1.  Simplicity: All the other python packages I've looked at each matcher is a class or something that needs to be registered via a more or less complicated process, arguments are not just straightforward method arguments, `not` is not supported as a native framework package...
    
    In contrast in pyexpect if you want to register a new matcher, it's as easy as defining a method and then assigning it to as many instance method names as you want:
    
        def my_matcher(self, all, the, arguments='I want'):
            pass # whatever you have to do. For helpers and availeable values see expect() source
        expect.new_matcher = expect.new_matcher_alias = my_matcher
    
    Done!

1.  Great error messages: pyexpect takes great care to ensure every aspect of experiencing an error is as concise and usefull as possible. All error messages have the same format that always starts with what is expected and then is customized by the matcher to pack as much information as possible.
    
        expect(23).not_.equals(23)
        Expect 23 not to equal 23
    
    If you write your own assertion methods to enhance your unit testing, it's quite easy to get long stack traces because the actuall assertion happens some stack frames down in one of the called matchers.
    
    Consider this code:
    
        from unittest import TestCase, main
        class Test(TestCase):
            def assert_equals(self, actual, expected):
                self.assertEquals(actual, expected)
            def assert_something(self, something):
                self.assert_equals(something, 'something')
            def test_something(self):
                self.assert_something('fnord')
        main()
    
    That will give you output like this:
    
        FAIL: test_something (__main__.Test)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          method test_something in test.py at line 11
            self.assert_something('fnord')
          method assert_something in test.py at line 8
            self.assert_equals(something, 'something')
          method assert_equals in test.py at line 5
            self.assertEquals(actual, expected)
        AssertionError: 'fnord' != 'something'
    
    Even in this simple case the actual error is 4 lines removed from the actual error.
    
    In pyexpect however a test like this:
    
        from pyexpect import expect
        def is_something(self):
            self._assert(self._expected == 'something', "to be something")
        expect.is_something = is_something
        
        from unittest import TestCase, main
        class Test(TestCase):
            def test_something(self):
                expect('fnord').is_something()
        main()
    
    Gives you this output (standard `unittest.main()`):
    
        FAIL: test_something (__main__.Test)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "test_example.py", line 11, in test_something
            expect('fnord').is_something()
          File "/Users/dwt/Code/Projekte/python-expect/pyexpect.py", line 150, in __call__
            raise assertion
        AssertionError: Expect 'fnord' to be something
    
    In `nosetests`:
        
        FAIL: test_example:Test.test_something
          mate +11  test_example.py  # test_something
            expect('fnord').is_something()
          mate +150 pyexpect.py  # __call__
            raise assertion
        AssertionError: Expect 'fnord' to be something
        
    `py.test` this is even prettier:
        
        self = <test_example.Test testMethod=test_something>
        def test_something(self):
        >       expect('fnord').is_something()
        E       AssertionError: Expect 'fnord' to be something
    

1.  Completeness: You can use this package as a standalone assertion package that gives you much more expressive assertions than just using using `assert` and refined error messages to boot.
    
    Just assert away wherever you need it to get robust code by failing fast:
    
        from pyexpect import expect
        def some_method(some_argument):
            expect(some_argument).is_within_range(3,20)
            something(some_argument)
    
    And should you need it, you can switch the assertions from throwing to returning a `(bool, string)` tuple so you can reuse it in your api.
    
        from pyexpect import expect
        def some_api(something):
            was_success, explanation = expect.returning(something) == 23
            if not was_success: register_error(explanation)
    
    And should you need it, you can override the error messages generated without needing to change the matchers. See `expect.with_message()` for details.

1.  Test coverage: Of course pyexpect has full test coverage ensuring that it does exactly what you expect it to do.