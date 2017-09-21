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


class TextInputPopup(amwidgets.Frame):
    """A fixed implementation Frame that prompts the user for input."""

    palette = amwidgets.PopUpDialog.palette

    def __init__(self, screen, prompt, label, on_ok=None, on_cancel=None,
                 has_shadow=False):
        # Enforce API requirements
        assert on_ok is None or type(on_ok) == FunctionType, \
            "on_ok must be a static fn"
        assert on_cancel is None or type(on_cancel) == FunctionType, \
            "on_cancel must be a static fn"

        self.prompt = prompt
        self.label = label
        self.text = ""
        self.on_ok = on_ok
        self.on_cancel = on_cancel

        # Decide on optimum width of the dialog.  Limit to 2/3 the screen width.
        width = max([amwidgets.wcswidth(x) for x in prompt.split("\n")])
        width = max(width + 4,
                    sum([amwidgets.wcswidth(x) + 4 for x in ("ok", "cancel")]) + 2 + 5)
        width = min(width, screen.width * 2 // 3)

        # Figure out the necessary message and allow for buttons and borders
        # when deciding on height.
        self._prompt = amwidgets._split_text(prompt, width - 4, screen.height - 4)
        height = len(self._prompt) + 4

        self._data = {"prompt": self._prompt, "input": self.text}

        super().__init__(
            screen, height, width, data=self._data, has_shadow=has_shadow)

        top = amwidgets.Layout([1], fill_frame=True)
        self.add_layout(top)
        prompt = amwidgets.TextBox(height=len(self._prompt), name="prompt")
        prompt.disabled = True
        top.add_widget(prompt)

        mid = amwidgets.Layout([1])
        self.add_layout(mid)
        input_box = amwidgets.Text(label=label, name="input")
        mid.add_widget(input_box)

        bottom = amwidgets.Layout([1, 1])
        self.add_layout(bottom)
        bottom.add_widget(amwidgets.Button("ok", None), 0)
        bottom.add_widget(amwidgets.Button("cancel", None), 1)
        self.fix()
