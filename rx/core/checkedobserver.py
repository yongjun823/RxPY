from rx.internal import extensionmethod
from rx.internal.exceptions import ReEntracyException, CompletedException

from . import Observer


class CheckedObserver(Observer):

    def __init__(self, observer):
        self._observer = observer
        self._state = 0  # 0 - idle, 1 - busy, 2 - done

    def send(self, value):
        self.check_access()
        try:
            self._observer.send(value)
        finally:
            self._state = 0

    def throw(self, error):
        self.check_access()
        try:
            self._observer.throw(error)
        finally:
            self._state = 2

    def close(self):
        self.check_access()
        try:
            self._observer.close()
        finally:
            self._state = 2

    def check_access(self):
        """Checks access to the observer for grammar violations.

        OnNext* (OnError | OnCompleted)?
        """

        if self._state == 1:
            raise ReEntracyException()
        if self._state == 2:
            raise CompletedException()
        if self._state == 0:
            self._state = 1


@extensionmethod(Observer)
def checked(self):
    """Checks access to the observer for grammar violations. This includes
    checking for multiple OnError or OnCompleted calls, as well as
    reentrancy in any of the observer methods. If a violation is detected,
    an Error is thrown from the offending observer method call.

    Returns an observer that checks callbacks invocations against the
    observer grammar and, if the checks pass, forwards those to the
    specified observer."""

    return CheckedObserver(self)
