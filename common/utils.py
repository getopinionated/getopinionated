def overrides(interface_class):
    """ overrides annotation from Stack Overflow:
    http://stackoverflow.com/a/8313042/1218058

    Usage:
        class MySuperInterface(object):
            def my_method(self):
                print 'hello world!'


        class ConcreteImplementer(MySuperInterface):
            @overrides(MySuperInterface)
            def my_method(self):
                print 'hello kitty!'

        and if you do a faulty version it will raise an assertion error during class loading:

        class ConcreteFaultyImplementer(MySuperInterface):
            @overrides(MySuperInterface)
            def your_method(self):
                print 'bye bye!'

        >> AssertionError!!!!!!!
    """
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider