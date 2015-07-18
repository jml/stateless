# Cribbed from https://github.com/python-effect/effect, which is MIT license.

from functools import partial, wraps
import sys
import types

from ._state import pure


def do(f):
    """
    A decorator which allows you to use ``do`` notation in your functions, for
    imperative-looking code::

        @do
        def foo():
            thing = yield get
            yield put(f(thing))
            yield do_return('result')

        eff = foo()
        return eff.bind(...)

    (This decorator is named for Haskell's ``do`` notation, which is similar in
    spirit).
    """
    @wraps(f)
    def do_wrapper(*args, **kwargs):
        gen = f(*args, **kwargs)
        if not isinstance(gen, types.GeneratorType):
            raise TypeError(
                "%r is not a generator function. It returned %r."
                % (f, gen))
        return _do(gen, None)
    return do_wrapper


class _ReturnSentinel(object):
    def __init__(self, result):
        self.result = result


def do_return(val):
    """
    Specify a return value for a @do function.

    The result of this function must be yielded.  e.g.::

        @do
        def foo():
            yield do_return('hello')

    If you're writing Python 3-only code, you don't need to use this function,
    and can just use the `return` statement as normal.
    """
    return _ReturnSentinel(val)


def _do(generator, result):
    try:
        val = generator.send(result)
    except StopIteration as stop:
        # If the generator we're spinning directly raises StopIteration, we'll
        # treat it like returning None from the function. But there may be a
        # case where some other code is raising StopIteration up through this
        # generator, in which case we shouldn't really treat it like a function
        # return -- it could quite easily hide bugs.
        tb = sys.exc_info()[2]
        if tb.tb_next:
            raise
        else:
            # Python 3 allows you to use `return val` in a generator, which
            # will be translated to a `StopIteration` with a `value` attribute
            # set to the return value. So we'll return that value as the
            # ultimate result of the effect. Python 2 doesn't have the 'value'
            # attribute of StopIteration, so we'll fall back to None.
            return pure(getattr(stop, 'value', None))
    if type(val) is _ReturnSentinel:
        return pure(val.result)
    else:
        bind = getattr(val, 'bind')
        if bind:
            return bind(partial(_do, generator))
        else:
            raise TypeError(
                "@do functions must only yield bindable things or results of do_return. "
                "Got %r from %r" % (val, generator))
