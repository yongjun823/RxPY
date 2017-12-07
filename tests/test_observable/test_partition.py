import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def is_even(num):
    return +num % 2 == 0


class TestPartition(unittest.TestCase):
    def test_partition_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            close(210)
        )

        subscription1 = [None]
        subscription2 = [None]
        observables = []

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()
        results1.messages.assert_equal(
            close(210)
        )

        results2.messages.assert_equal(
            close(210)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 210)
        )

    def test_partition_single(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            close(220)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4),
            close(220)
        )

        results2.messages.assert_equal(
            close(220)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 220)
        )

    def test_partition_each(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(220, 3),
            close(230)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4),
            close(230)
        )

        results2.messages.assert_equal(
            send(220, 3),
            close(230)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 230)
        )

    def test_partiticlose(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1),
            close(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)
        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4),
            send(290, 2),
            close(360)
        )

        results2.messages.assert_equal(
            send(240, 3),
            send(350, 1),
            close(360)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 360)
        )

    def test_partition_not_completed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]

        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4),
            send(290, 2)
        )

        results2.messages.assert_equal(
            send(240, 3),
            send(350, 1)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

    def test_partitithrow(self):
        error = Exception()
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            throw(290, error),
            send(350, 1),
            close(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))
        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(ReactiveTest.disposed, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4),
            throw(290, error)
        )

        results2.messages.assert_equal(
            send(240, 3),
            throw(290, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 290)
        )

    def test_partition_disposed(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(180, 5),
            send(210, 4),
            send(240, 3),
            send(290, 2),
            send(350, 1),
            close(360)
        )

        observables = []
        subscription1 = [None]
        subscription2 = [None]
        results1 = scheduler.create_observer()
        results2 = scheduler.create_observer()

        def action0(scheduler, state):
            observables.extend(xs.partition(is_even))

        scheduler.schedule_absolute(ReactiveTest.created, action0)

        def action1(scheduler, state):
            subscription1[0] = observables[0].subscribe(results1)
            subscription2[0] = observables[1].subscribe(results2)

        scheduler.schedule_absolute(ReactiveTest.subscribed, action1)

        def action2(scheduler, state):
            subscription1[0].dispose()
            subscription2[0].dispose()
        scheduler.schedule_absolute(280, action2)

        scheduler.start()

        results1.messages.assert_equal(
            send(210, 4)
        )

        results2.messages.assert_equal(
            send(240, 3)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 280)
        )
