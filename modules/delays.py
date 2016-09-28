from constants import TICKRATE
from internal_events import InternalEvent


tick_number = 0
delays = []


class Delay:
    def __init__(self, seconds, callback, args=(), kwargs=None):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs or {}

        self.running = True
        self.fires_at = tick_number + seconds * TICKRATE

        delays.append(self)

    def __call__(self):
        self.running = False
        self.callback(*self.args, **self.kwargs)

    def cancel(self):
        if self.running:
            delays.remove(self)


def on_tick():
    global tick_number
    tick_number += 1

    for delay in list(delays):
        if delay.fires_at <= tick_number:
            delay()
            delays.remove(delay)


@InternalEvent('load')
def on_load(app):
    app.register_tick_listener(on_tick)
