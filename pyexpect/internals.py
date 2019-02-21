import sys
from contextlib import contextmanager

__unittest = True # Hide from unittest.TestCase

def remove_internals_from_assertion_backtraces(method_to_be_wrapped):
    # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
    # Hides the actual matcher and all the methods it calls to assert stuff.
    # Sadly there seems to be no better way to controll exception stack traces.
    # If you have a good idea how to improve this, please tell me!
    def pyexpect_internals_hidden_in_backtraces(*args, **kwargs):
        __tracebackhide__ = True  # Hide from py.test tracebacks
        if hasattr(remove_internals_from_assertion_backtraces, 'disabled'):
            return method_to_be_wrapped(*args, **kwargs)
        
        try:
            return method_to_be_wrapped(*args, **kwargs)
        except AssertionError as exception:
            is_python3 = sys.version > '3'
            if is_python3: # refact: would it be better to just check for hasattr(exception, '__cause__')?
                # Get rid of the link to the causing exception as it greatly cluttes the error message
                exception.__cause__ = None
                exception.with_traceback(None)
            raise exception # use `with expect.disabled_backtrace_cleaning():` to show full backtrace
    return pyexpect_internals_hidden_in_backtraces


def alias_with_hidden_backtrace(public_name):
    """Works around the problem that special methods (as in '__something__') are not resolved
    using __getattribute__() and thus do not provide the nice tracebacks that they public matchers provide.
    
    This method works on the class dict and is repeated after each instantiation
    to support adding or overwriting existing matchers at any time while not repeatedly doing the same.
    """
    @remove_internals_from_assertion_backtraces
    def wrapper(self, *args, **kwargs):
        self.__getattribute__(public_name)(*args, **kwargs)
    return wrapper




class ExpectMetaMagic(object):
    
    ## Internals ########################################################################################
    # REFACT: consider to find a way to separate them better from the matchers. Maybe move to a different
    # file and include as a superclass? Could even access the attributes via the class object directly to get rid of much of the __getattribute__ hack?
    
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
        
        def _has_attr(name):
            "Need custom hasattr to prevent recursion with __getattribute__"
            try:
                object.__getattribute__(self, name)
                return True
            except AttributeError as e:
                return False
        
        # some matchers need _ suffix to prevent colision with python keywords
        if not _has_attr(name) and _has_attr(name + '_'):
            name += '_'
        
        # need object.__getattribute__ to prevent recursion with self.__getattribute__
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            return None
    
    def _prepare_matcher_for_calling(self, name, matcher):
        self._selected_matcher_name = name
        self._selected_matcher = matcher
    
    @remove_internals_from_assertion_backtraces
    def __call__(self, *args, **kwargs):
        """Called whenever you actualy invoke a matcher. 
        
        Provides a good error message if you mistype the matcher name.
        
        Supports custom messages with the message keyword argument"""
        
        # TODO would be nice if this could show the availeable matchers and propose something where the spelling is close 'did you mean xxx'
        # When listing availeable matchers, they should be groupdd by aliasses
        if self._selected_matcher is None:
            raise NotImplementedError("Tried to call non existing matcher '{0}' (Patches welcome!)".format(self._selected_matcher_name))
        
        try:
            return_value = self._selected_matcher(*args, **kwargs)
            # allow an otherwise raising matcher to return something
            # usefull for matchers like expect.to_raise() to return the caught exception for further analysis
            if self._should_raise:
                return return_value
        except AssertionError as assertion:
            message = self._force_utf8(assertion)
            
            if self._should_raise:
                raise
            
            return (False, message)
        
        return (True, "")
    
    def _assert(self, assertion, message_format, *message_positionals, **message_keywords):
        # FIXME assertions will be disabled in python -o 1 - so this my be no good if pyexpect is used as an expectation library in production code. See https://github.com/pyca/cryptography/commit/915e0a1194400203b0e49e05de5facbc4ac8eb66
        assert assertion is self._expected_assertion_result, \
            self._message(message_format, message_positionals, message_keywords)
    
    def _assert_if_positive(self, assertion, message_format, *message_positionals, **message_keywords):
        if self._is_negative():
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _assert_if_negative(self, assertion, message_format, *message_positionals, **message_keywords):
        if not self._is_negative():
            return
        
        self._assert(assertion, message_format, *message_positionals, **message_keywords)
    
    def _message(self, message_format, message_positionals, message_keywords):
        message = self._force_utf8(message_format).format(*message_positionals, **message_keywords)
        actual = repr(self._actual)
        # using two newlines to make it easier to find on a terminal
        optional_newline = '\n\n' if len(actual) > 40 else ' '
        optional_negation = 'not ' if self._is_negative() else ''
        assertion_message = "Expect {actual}{optional_newline}{optional_negation}{message}".format(**locals())
        
        if self._custom_message is not None:
            return self._custom_message.format(**locals())
        
        return assertion_message
    
    def _force_utf8(self, exception):
        if sys.version < '3':
            try: return unicode(exception).encode('utf8')
            except UnicodeDecodeError as ignored: pass
        
        return str(exception)
    
    def _is_negative(self):
        return self._expected_assertion_result is False
    
    def _concatenate(self, *args):
        return args
    
    @staticmethod
    @contextmanager
    def disabled_backtrace_cleaning():
        remove_internals_from_assertion_backtraces.disabled = True
        try:
            yield
        finally:
            del remove_internals_from_assertion_backtraces.disabled
    
