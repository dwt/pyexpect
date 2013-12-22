## Minimal but very flexible implementation of the expect pattern.

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