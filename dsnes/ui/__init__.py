# Copyright 2017 Adrian Chan
# Licensed under GPLv3

from asciimatics.screen import Screen
from asciimatics.scene import Scene
import asciimatics.exceptions

import dsnes
from dsnes.ui.startpage import StartPage


SHOW_FOREVER = -1


def start():
    session = dsnes.interactive.Session()
    last_scene = None

    def ui(screen, start_scene=None):
        scenes = [
            Scene([dsnes.ui.StartPage(screen, session)],
                  duration=SHOW_FOREVER, name="Start Page")
        ]
        screen.play(scenes, stop_on_resize=True, start_scene=start_scene)

    while True:
        try:
            Screen.wrapper(ui, arguments=[last_scene])
            break
        except asciimatics.exceptions.ResizeScreenError as ex:
            last_scene = ex.scene
