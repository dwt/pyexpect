import sys

def remove_internals_from_assertion_backtraces(method_to_be_wrapped):
    # Make the stacktrace easier to read by tricking python to shorten the stack trace to this method.
    # Hides the actual matcher and all the methods it calls to assert stuff.
    # Sadly there seems to be no better way to controll exception stack traces.
    # If you have a good idea how to improve this, please tell me!
    def pyexpect_internals_hidden_in_backtraces(*args, **kwargs):
        try:
            return method_to_be_wrapped(*args, **kwargs)
        except AssertionError as exception:
            is_python3 = sys.version > '3'
            if is_python3:
                # Get rid of the link to the causing exception as it greatly cluttes the error message
                exception.__cause__ = None
                exception.with_traceback(None)
            raise exception
    return pyexpect_internals_hidden_in_backtraces


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
        __tracebackhide__ = True  # Hide from py.test tracebacks
        
        if self._selected_matcher is None:
            raise NotImplementedError("Tried to call non existing matcher '{0}' (Patches welcome!)".format(self._selected_matcher_name))
        
        try:
            return_value = self._selected_matcher(*args, **kwargs)
            # allow an otherwise raising matcher to return something
            # usefull for matchers like expect.to_raise() to return the caught exception for further analysis
            if self._should_raise:
                return return_value
        except AssertionError as assertion:
            # REFACT: consider to do this when creating the assertion as that's the most logical place to look for it
            message = self._message(assertion)
            
            if self._should_raise:
                raise AssertionError(message)
            
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
        actual = repr(self._actual)
        # using two newlines to make it easier to find on a terminal
        optional_newline = '\n\n' if len(actual) > 30 else ' '
        optional_negation = 'not ' if self._is_negative() else ''
        assertion_message = "Expect {actual}{optional_newline}{optional_negation}{message}".format(**locals())
        
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
            @remove_internals_from_assertion_backtraces
            def wrapper(self, *args, **kwargs):
                __tracebackhide__ = True  # Hide from py.test tracebacks
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
    

