import collections
import functools

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


def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func
