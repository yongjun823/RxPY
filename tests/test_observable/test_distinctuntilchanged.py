import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestDistinctUntilChanged(unittest.TestCase):
    def test_distinct_until_changed_never(self):
        scheduler = TestScheduler()

        def create():
            return Observable.never().distinct_until_changed()
        results = scheduler.start(create)

        results.messages.assert_equal()

    def test_distinct_until_changed_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(250))

        def create():
            return xs.distinct_until_changed()

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'C' and results[0].time == 250)

    def test_distinct_until_changed_return(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(220, 2), close(250))

        def create():
            return xs.distinct_until_changed()
        results = scheduler.start(create).messages
        self.assertEqual(2, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 220 and results[0].value.value == 2)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_distinct_until_changed_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(250, ex))

        def create():
            return xs.distinct_until_changed()

        results = scheduler.start(create).messages
        self.assertEqual(1, len(results))
        assert(results[0].value.kind == 'E' and results[0].time == 250 and results[0].value.exception == ex)

    def test_distinct_until_changed_all_changes(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(220, 3),
            send(230, 4),
            send(240, 5),
            close(250))

        def create():
            return xs.distinct_until_changed()

        results = scheduler.start(create).messages
        self.assertEqual(5, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'N' and results[1].time == 220 and results[1].value.value == 3)
        assert(results[2].value.kind == 'N' and results[2].time == 230 and results[2].value.value == 4)
        assert(results[3].value.kind == 'N' and results[3].time == 240 and results[3].value.value == 5)
        assert(results[4].value.kind == 'C' and results[4].time == 250)

    def test_distinct_until_changed_all_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 2), send(230, 2), send(240, 2), close(250))

        def create():
            return xs.distinct_until_changed()

        results = scheduler.start(create).messages
        self.assertEqual(2, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_distinct_until_changed_some_changes(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(215, 3), send(220, 3), send(225, 2), send(230, 2), send(230, 1), send(240, 2), close(250))

        def create():
            return xs.distinct_until_changed()

        results = scheduler.start(create).messages
        self.assertEqual(6, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'N' and results[1].time == 215 and results[1].value.value == 3)
        assert(results[2].value.kind == 'N' and results[2].time == 225 and results[2].value.value == 2)
        assert(results[3].value.kind == 'N' and results[3].time == 230 and results[3].value.value == 1)
        assert(results[4].value.kind == 'N' and results[4].time == 240 and results[4].value.value == 2)
        assert(results[5].value.kind == 'C' and results[5].time == 250)

    def test_distinct_until_changed_comparer_all_equal(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), send(230, 4), send(240, 5), close(250))

        def create():
            return xs.distinct_until_changed(comparer=lambda x, y: True)

        results = scheduler.start(create).messages
        self.assertEqual(2, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'C' and results[1].time == 250)

    def test_distinct_until_changed_comparer_all_different(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 2), send(230, 2), send(240, 2), close(250))

        def create():
            return xs.distinct_until_changed(comparer=lambda x, y: False)

        results = scheduler.start(create).messages
        self.assertEqual(5, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'N' and results[1].time == 220 and results[1].value.value == 2)
        assert(results[2].value.kind == 'N' and results[2].time == 230 and results[2].value.value == 2)
        assert(results[3].value.kind == 'N' and results[3].time == 240 and results[3].value.value == 2)
        assert(results[4].value.kind == 'C' and results[4].time == 250)

    def test_distinct_until_changed_key_selector_div2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 4), send(230, 3), send(240, 5), close(250))

        def create():
            return xs.distinct_until_changed(lambda x: x % 2)

        results = scheduler.start(create).messages
        self.assertEqual(3, len(results))
        assert(results[0].value.kind == 'N' and results[0].time == 210 and results[0].value.value == 2)
        assert(results[1].value.kind == 'N' and results[1].time == 230 and results[1].value.value == 3)
        assert(results[2].value.kind == 'C' and results[2].time == 250)

    def test_distinct_until_changed_key_selector_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), close(250))

        def create():
            return xs.distinct_until_changed(lambda x: _raise(ex))
        results = scheduler.start(create)
        results.messages.assert_equal(throw(210, ex))

    def test_distinct_until_changed_comparer_throws(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(210, 2), send(220, 3), close(250))

        def create():
            return xs.distinct_until_changed(comparer=lambda x,y: _raise(ex))

        results = scheduler.start(create)
        results.messages.assert_equal(send(210, 2), throw(220, ex))
