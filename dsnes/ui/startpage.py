# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from asciimatics.scene import Scene
from asciimatics.widgets import Button, Frame, Label, Layout

import dsnes


def StartPage(screen, session):
    return Scene(
        [StartPageFrame(screen, session)],
        duration=dsnes.ui.SHOW_FOREVER, name=dsnes.ui.START_PAGE)


class StartPageFrame(Frame):

    def __init__(self, screen, session):
        super().__init__(
            screen, screen.height, screen.width,
            on_load=None, has_border=True, hover_focus=True,
            title="dSNES")

        self.screen = screen
        self.session = session

        layout = Layout([1, 1])
        self.add_layout(layout)
        layout.add_widget(Button("TODO: New Project", None, "a label?"))
        layout.add_widget(Button("TODO: Load Project", None))
        layout.add_widget(Button("Test Popup", self.do_test_popup), 1)
        self.fix()

    def do_test_popup(self):
        self._scene.add_effect(
            dsnes.ui.widgets.TextInputPopup(self.screen, "prompt goes here", "Address"))
