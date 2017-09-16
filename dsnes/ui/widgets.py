# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import queue

from asciimatics import widgets as amwidgets


class BetterFrame(amwidgets.Frame):
    """An asciimatics Frame with extended capabilities.

    Has a user event queue and the ability to hide the frame.
    """

    def __init__(self, *args, hidden=False, **kwargs):
        assert hidden in (True, False)
        self.user_event_queue = queue.Queue()
        self.hidden = hidden
        super().__init__(*args, **kwargs)

    def hide(self):
        self.hidden = True
        self._screen.force_update()

    def show(self):
        self.hidden = False
        self._screen.force_update()

    def _update(self, frame_no):
        self.process_user_event_queue()
        if not self.hidden:
            super()._update(frame_no)

    def process_event(self, event):
        if self.hidden:
            return event
        else:
            return super().process_event(event)

    def process_user_event_queue(self):
        while True:
            try:
                callback = self.user_event_queue.get_nowait()
                callback()
            except queue.Empty:
                break

    def do_in_gui(self, callback):
        self.user_event_queue.put_nowait(callback)
        self._screen.force_update()

    @property
    def is_hidden(self):
        return self.hidden
