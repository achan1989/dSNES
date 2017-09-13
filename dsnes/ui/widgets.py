# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import queue

from asciimatics import widgets as amwidgets


class EventFrame(amwidgets.Frame):
    """Extend the asciimatics Frame with an event queue."""

    def __init__(self, *args, **kwargs):
        self.event_queue = queue.Queue()
        super().__init__(*args, **kwargs)

    def _update(self, frame_no):
        self.process_event_queue()
        super()._update(frame_no)

    def process_event_queue(self):
        while True:
            try:
                callback = self.event_queue.get_nowait()
                callback()
            except queue.Empty:
                break

    def do_in_gui(self, callback):
        self.event_queue.put_nowait(callback)
        self._screen.force_update()

