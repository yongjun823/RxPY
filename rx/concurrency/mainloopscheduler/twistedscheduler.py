import logging
from datetime import datetime, timedelta

from rx.disposables import Disposable, SingleAssignmentDisposable, \
    CompositeDisposable
from rx.concurrency.scheduler import Scheduler
from rx.internal.basic import default_now

log = logging.getLogger("Rx")

class TwistedScheduler(Scheduler):
    """A scheduler that schedules work via the asyncio mainloop."""

    def __init__(self, reactor):
        self.reactor = reactor

    def schedule(self, action, state=None):
        return self.schedule_relative(0, action, state)
        
    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {timedelta} Relative time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        scheduler = self
        seconds = TwistedScheduler.normalize(duetime)
        
        disposable = SingleAssignmentDisposable()
        def interval():
            disposable.disposable = action(scheduler, state)

        log.debug("timeout: %s", seconds)
        handle = [self.reactor.callLater(seconds, interval)]

        def dispose():
            handle[0].cancel()

        return CompositeDisposable(disposable, Disposable(dispose))

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime.

        Keyword arguments:
        duetime -- {datetime} Absolute time after which to execute the action.
        action -- {Function} Action to be executed.

        Returns {Disposable} The disposable object used to cancel the scheduled
        action (best effort)."""

        return self.schedule_relative(duetime - self.now(), action, state)

    def now(self):
        """Represents a notion of time for this scheduler. Tasks being scheduled 
        on a scheduler will adhere to the time denoted by this property."""
        
        return self.to_datetime(self.reactor.seconds()*1000)

