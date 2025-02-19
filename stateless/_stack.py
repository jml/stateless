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

"""
Stack implementation using stateful actions.
"""

from pyrsistent import v

from ._state import (
    get,
    pure,
    put,
    run,
)


def push(x):
    return get.bind(lambda stack: put(stack.append(x)))


pop = get.bind(lambda stack: put(stack[:-1]).then(pure(stack[-1])))


def stackful(computation, initial=v()):
    return run(computation, initial)
