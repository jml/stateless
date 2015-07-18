# Copyright (c) 2015 Jonathan M. Lange <jml@mumak.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyrsistent import field, PClass


class _State(PClass):
    """
    An action that, given an initial state, returns a value and a new state.
    """

    _function = field()

    @classmethod
    def new(cls, function):
        """
        Create a new stateful action.

        :param function: a callable that takes a single parameter representing
            the initial state and returns a tuple of ``(a, new_state)``, where
            ``a`` is the result of the action and ``new_state`` is the new
            state.
        :return: A stateful action.
        """
        return cls(_function=function)

    def run(self, state):
        """
        Run this action given initial state ``state``.

        :return: A tuple of ``(a, s)``, where ``a`` is the value of the action,
            and ``s`` is the new state.
        """
        return self._function(state)

    def map(self, function):
        return map_state(self, function)

    def bind(self, function):
        return bind(self, function)

    def then(self, new_state):
        return then(self, new_state)


def pure(value):
    """
    Create a stateful action that does not use the state at all.

    :return: A ``State`` that when run will return ``value`` as-is and the
        state unchanged.
    """
    return _State.new(lambda s: (value, s))


def run(state, initial):
    """
    Run the stateful action ``state`` given initial state ``initial``.

    Equivalent to ``state.run(initial)``.

    :return: A tuple of ``(a, s)``, where ``a`` is the value of the action,
        and ``s`` is the new state.
    """
    return state.run(initial)


def evaluate(state, initial):
    """
    Evaluate ``state`` given initial state ``initial``.

    :return: The value of the action.
    """
    return run(state, initial)[0]


def execute(state, initial):
    """
    Execute ``state`` given initial state ``initial``.

    :return: The new state.
    """
    return run(state, initial)[1]


def map_state(state, function):
    """
    Map the value of ``state`` with ``function``, without reference to the
    actual state.
    """
    def _new_operation(s):
        a, s2 = run(state, s)
        return pure(function(a))
    return state.new(_new_operation)


def bind(state, function):
    """
    Bind ``function`` to the stateful action ``state``.

    ``function`` must expect a single parameter. It will be called with
    the value of this stateful action.

    :param state: A stateful action that returns a value of type ``A`` and
        state ``S``.
    :param function: A function that expects a single parameter of type ``A``
        and returns a ``State`` wrapper for state ``S`` and value of
        type ``B``.
    :return: A State wrapper for a state ``S`` and value of type ``B``.
    """
    def _new_operation(s):
        a, s2 = run(state, s)
        return function(a).run(s2)
    return state.new(_new_operation)


# XXX: Rather than making up my own terminology, I should probably borrow from
# Rust, which at least has words for these things.
def then(state1, state2):
    """
    Like ``bind``, but instead of a function that returns a statetful action,
    just bind a new stateful action.

    Equivalent to bind(state1, lambda _: state2)
    """
    return bind(state1, lambda _: state2)


def put(new_state):
    """
    A stateful action that replaces the current state with ``new_state``.
    """
    return _State.new(lambda _: (None, new_state))


"""
A stateful action that retrieves the current state.
"""
get = _State.new(lambda s: (s, s))


def modify(function):
    """
    A stateful action that updates the state to the result of applying
    ``function`` to the current state.

    :param function: A unary callable.
    """
    return get().map(function).bind(put)
