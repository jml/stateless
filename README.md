# stateless

Experimental library for doing stateful computations in Python without
actually assigning to anything.

I'm not exactly sure why you would want to use this.

## Example #1 - Increment state

A stateful action that increments the current state.

```python
from stateless import *

increment = get.bind(lambda x: put(x + 1))

print(run(increment, 5))
```

The result is `(None, 6)`.


## Example #2 - Increment twice

```python
increment_twice = increment.then(increment)

print(run(increment_twice, 5))
```

Result: `(None, 7)`

## Example #3 - Fizzbuzz

```python
def fizzbuzz(n):
    if n % 15 == 0:
        return 'fizzbuzz'
    elif n % 5 == 0:
        return 'buzz'
    elif n % 3 == 0:
        return 'fizz'

fizzbuzzer = increment.then(get).map(fizzbuzz)

print(run(fizzbuzzer, 4))
print(run(fizzbuzzer, 14))
```

## Example #4 - Stacks

```python

op = push(5).then(push(4)).then(pop).bind(lambda x: push(2 * x))

print(stackful(op))
```

Result: `(None, pvector([5, 8]))`

## Example #5 - do notation

```python

@do
def _stack_multiply():
    a = yield pop
    b = yield pop
    yield push(a * b)

stack_multiply = stack_multiply()

op = push(5).then(push(4)).then(stack_multiply).then(pop)

print(stackful(op))
```

Result: `(20, pvector([]))`
