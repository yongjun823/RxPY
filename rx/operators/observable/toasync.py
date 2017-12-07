from rx.core import Observable
from rx.concurrency import timeout_scheduler
from rx.subjects import AsyncSubject
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable)
def to_async(cls, func, scheduler=None):
    """Converts the function into an asynchronous function. Each invocation
    of the resulting asynchronous function causes an invocation of the
    original synchronous function on the specified scheduler.

    Example:
    res = Observable.to_async(lambda x, y: x + y)(4, 3)
    res = Observable.to_async(lambda x, y: x + y, Scheduler.timeout)(4, 3)
    res = Observable.to_async(lambda x: log.debug(x),
                              Scheduler.timeout)('hello')

    func -- {Function} Function to convert to an asynchronous function.
    scheduler -- {Scheduler} [Optional] Scheduler to run the function on. If
        not specified, defaults to Scheduler.timeout.

    Returns {Function} Asynchronous function.
    """

    scheduler =  scheduler or timeout_scheduler

    def wrapper(*args):
        subject = AsyncSubject()

        def action(scheduler, state):
            try:
                result = func(*args)
            except Exception as ex:
                subject.throw(ex)
                return

            subject.send(result)
            subject.close()

        scheduler.schedule(action)
        return subject.as_observable()
    return wrapper
