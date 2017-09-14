# Copyright 2017 Adrian Chan
# Licensed under GPLv3

import threading

from asciimatics.scene import Scene
from asciimatics.widgets import Button, Frame, Label, Layout
from asciimatics.exceptions import NextScene

import dsnes
from .widgets import EventFrame


def AnalysisPage(screen, session):
    menu_height = 10
    view_height = screen.height - menu_height
    return Scene(
        [ViewFrame(screen, view_height, screen.width, session),
         MenuFrame(screen, menu_height, screen.width, session)],
        duration=dsnes.ui.SHOW_FOREVER, name=dsnes.ui.ANALYSIS_PAGE)


class ViewFrame(EventFrame):

    def __init__(self, screen, height, width, session):
        super().__init__(
            screen, height, width, y=0,
            on_load=None, has_border=True)

        self.screen = screen
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label("Analysis output goes here..."), 1)
        self.fix()


class MenuFrame(EventFrame):

    def __init__(self, screen, height, width, session):
        super().__init__(
            screen, height, width, y=screen.height-height,
            on_load=None, has_border=True)

        self.screen = screen
        self.session = session

        layout = Layout([1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label("Analysis menu goes here..."), 1)
        self.fix()
