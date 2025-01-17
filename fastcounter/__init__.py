import itertools
import threading

import cython


class Counter(object):
    """A counter that is only suitable for application without any concurrency."""

    __slots__ = (
        "value",
        "_step",
    )

    def __init__(self, init: int = 0, step: int = 1):
        self.value = init
        self._step = step

    def increment(self, num_steps: int = 1) -> None:
        self.value += self._step * num_steps


class FastReadCounter(Counter):
    __slots__ = (
        "value",
        "_lock",
        "_step",
    )

    def __init__(self, init: int = 0, step: int = 1):
        super().__init__(init, step)
        self._lock = threading.Lock()

    def increment(self, num_steps: int = 1) -> None:
        with self._lock:
            self.value += self._step * num_steps


class FastWriteCounter(Counter):
    __slots__ = (
        "_number_of_read",
        "_counter",
        "_lock",
        "_step",
    )

    def __init__(self, init: int = 0, step: int = 1):
        self._number_of_read = 0
        self._step = step
        self._counter = itertools.count(init, step)
        self._lock = threading.Lock()

    def increment(self, num_steps: int = 1) -> None:
        for i in range(0, num_steps):
            next(self._counter)

    @property
    def value(self) -> int:
        with self._lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += self._step
        return value

    @value.setter
    def value(self, _: int) -> None:
        raise Exception(f"Cannot set value of {type(self)}")


@cython.cclass
class CyCounter:
    """A Cython counter that is only suitable for application without any concurrency."""

    value = cython.declare(cython.bint, visibility="public")
    _step: int

    def __init__(self, init: int = 0, step: int = 1):
        self.value = init
        self._step = step

    @cython.ccall
    def increment(self, num_steps: int = 1) -> cython.void:
        self.value += self._step * num_steps


@cython.cclass
class CyFastReadCounter:
    """A Cython fast read counter that is suitable for application with concurrency."""

    # value is public
    value = cython.declare(cython.bint, visibility="public")
    _step: int
    _lock: threading.Lock

    def __init__(self, init: int = 0, step: int = 1):
        self.value = init
        self._step = step
        self._lock = threading.Lock()

    @cython.ccall
    def increment(self, num_steps: int = 1) -> cython.void:
        with self._lock:
            self.value += self._step * num_steps


@cython.cclass
class CyFastWriteCounter:
    """A Cython fast write counter that is suitable for application with concurrency."""

    _number_of_read: int
    _counter: itertools.count
    _lock: threading.Lock
    _step: int

    def __init__(self, init: int = 0, step: int = 1):
        self._number_of_read = 0
        self._step = step
        self._counter = itertools.count(init, step)
        self._lock = threading.Lock()

    @cython.ccall
    def increment(self, num_steps: int = 1) -> cython.void:
        for _ in range(0, num_steps):
            next(self._counter)

    @property
    @cython.returns(cython.bint)
    def value(self) -> int:
        with self._lock:
            value = next(self._counter) - self._number_of_read
            self._number_of_read += self._step
        return value

    @value.setter
    def value(self, _: int) -> None:
        raise Exception(f"Cannot set value of {type(self)}")
