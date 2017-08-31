# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from asciimatics.widgets import Button, Frame, Label, Layout


class StartPage(Frame):

    def __init__(self, screen, session):
        super().__init__(
            screen, screen.height, screen.width,
            on_load=None, has_border=True, hover_focus=True,
            title="dSNES")

        self.screen = screen
        self.session = session

        layout = Layout([1, 1])
        self.add_layout(layout)
        layout.add_widget(Button("New Project", None, "a label?"))
        layout.add_widget(Button("Load Project", None))
        self.fix()
