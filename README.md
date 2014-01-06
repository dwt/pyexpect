# pyexpect: Minimal but very flexible implementation of the expect pattern

The whole point of the expect patter is to allow concise assertions that generate predictable and good error messages.

Best viewed in an example:

    >>> expect(3).to_equal(4)
    Traceback (most recent call last):
      File "<input>", line 1, in <module>
      File "expect.py", line 146, in __call__
    AssertionError: Expect 3 to be equal to 4

Line noise is reduced as much as possible, so the error message is displayed as near to the problematic code as possible. No stack traces to dig through, clear and consistent error messages that tell you what went wrong. Thats how assertions should work.

## Why should I use expect() over self.assert*?

This is best explained in cotrast to the classic assertion pattern like the python unittest module uses. However, these assertions can be used anywhere and do not depend on any unittest package. But now for the example:

    self.assertEquals('foo', 'bar')

In this assertion it is not possible to see which of the arguments is the expected and which is the actual value. While this ordering is mostly internally consistent within the unittest package (sadly only mostly), it is not consistent between all the different unit testing packages out there for python and especially not between different languages this pattern has been implemented on.

To add insult to injury some frameworks will then output the error message like this:
(Yes unittest I'm looking at you!)

    'bar' does not equal 'foo'

It's easy to spend minutes till you remember or figure out that your framework fooled you and inverted the order of arguments just to make it harder for you to understand the code you are reading.

If you are as annoyed by this as I am, allow me to introduce you to the expect pattern. An assertion like this:

    expect('foo').to.equal('bar')
    # or this
    expect('foo').equals('bar')
    # or even this
    expect('foo') == 'bar'

Makes it absolutely plain what is the expected and what is the actual value. 
No confusion possible. Also the error messages are designed to map cleanly back
to the source code:

    Expect 'foo' to equal 'bar'.

Thus the mapping from the error message is immediate and complete saving you minutes each time, enhancing your focus, productivity and - most important - your enjoyment when working with these expectations.

As a bonus they are not coupled to any TestCase class so you can easily reuse them anywhere in your code to formalize expectations that your code has about some internal state. Oh and they are shorter, so you even have less to write while getting clearer and more to the point assertions. Almost like having a cake and eating it too!

## So give me the features!

Glad you ask! Here you go

1.  Lots of included matchers. Take a look at the source to see all the assertions you need to get started. From `is_equal` over `to_be` and `to_raise` till `to_match` - we've got you covered. And not only that, but each matcher has some aliasses so you can use the variant that reads the best in your assertion. (If someting important is missing, pull requests are welcome.)

1.  Ease of use: `expect()` can be arbitrary chained with whatever you can think of (provided it's a valid python identifier) to give you the cleanest description of your assertion possible:
    
        expect(23).to.equal(23)
        expect(23).is_.equal(23)
        # or go all out - but just because it works doesn't mean it's sensible
        expect(23).to_be_chaned.with_something.that_makes_sense_in\
            .your_context.before_it.calls_the.matcher.equals(23)
    
    Matchers also have many aliasses defined to enable you to write the expectations in a natural way:
    
        expect(True).is_.true()
        expect(True).is_true()
        expect(True).is_equal(True)
        expect(True) == True
        expect(raising_calable).raises()
        expect(raising_calable).to_raise()
    
    Choose whatever makes sense for your specific test to read well so that reading the test later feels natural and transports the meaning of the code as best as possible. Should an important alias be missing, pull requests are welcome.

1.  Simplicity of extension: All the other python packages I've looked at each matcher is a class or something that needs to be registered via a more or less complicated process, arguments are not just straightforward method arguments, `not` is not supported as a native framework concept...
    
    In contrast in pyexpect if you want to register a new matcher, it's as easy as defining a method and then assigning it to as many instance method names as you want:
    
        def is_falseish(self):
            # whatever you have to do. For helpers and availeable values see expect() source
            self._assert(bool(self._expected) is False, "to be falseish")
        expect.is_falseish = is_falseish
    
    Done!

1.  Native `not` support: If you define a matcher, you don't have to define the inverse of it too or do anything special to get it. That means that for every matchers like `equals`, you automatically get the inverse of that, i.e. `not_equals`. This inverse can be invoked in a number of ways: 
    
    You can just prefix the matcher with `not_` like this
    
        expect(foo).not_equals(bar)
        expect(some_function).not_to_raise()
    
    You can include `not` as part of the path before the matcher like this:
    
        expect(foo).not_.to_equal(bar)
        expect(foo).not_to.equal(bar)
        expect(foo).to_not.equal(bar)
        expect(foo).to_not_be.equal(bar)
        # or go all out - but just because it works doesn't mean it's sensible
        expect(foo).is.just_a_little.not_quite_the_same_as_it.equals(bar)
    
    That is you can include the word `not` at the beginning, middle or end of an identifier - just ensure to separate it from the identifier by snakecase.
    
    This works for all aliasses of each matcher, so no additional work there.
    
    For more examples, have a look at the testsuite for the matchers.
    
    If you want to add your own matchers, sometimes the inverse doesn't work automatically if you implement your expectations with multiple checks. In that case the inverse matcher might assert the wrong thing, because the order of the checks doesn't make sense in the inverted case. Should that happen, take a look at  `expect._assert_if_positive()`, `expect._assert_if_negative()` and `expect._is_negative()`. Be advised however, that good matchers should need this only very rarely.

1.  Great error messages: pyexpect takes great care to ensure every aspect of experiencing an error is as concise and usefull as possible. All error messages have the same format that always starts with what is expected and then is customized by the matcher to pack as much information as possible.
    
        expect(23).not_to_equal(23)
        Expect 23 not to equal 23
    
    If you write your own assertion methods to enhance your unit testing, it's quite easy to get long stack traces because the actuall assertion happens some stack frames down in one of the called matchers.
    
    Consider assertions like this: (a little fabricated, but you get the idea)
    
        from unittest import TestCase, main
        class Test(TestCase):
            def assert_equals(self, actual, expected):
                self.assertEquals(actual, expected)
            def assert_something(self, something):
                self.assert_equals(something, 'something')
            def test_something(self):
                self.assert_something('fnord')
        main()
    
    It will give you output like this:
    
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
    
    That is, the error messages are much easier to read because there is less fluff in between that distracts you from your tests. As it should be.

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