# -*- coding: utf-8 -*-
# Copyright: Muneyuki Noguchi
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Adjust the sound volume in 2.1.20.
"""

from typing import Any

from anki.sound import AVTag
from aqt import gui_hooks
from aqt import mw
from aqt.sound import MpvManager
from aqt.sound import SimpleMplayerSlaveModePlayer
from aqt.qt import QAction
from aqt.qt import QDialog
from aqt.qt import QHBoxLayout
from aqt.qt import QSlider
from aqt.qt import QSpinBox
from aqt.qt import Qt

# Adjust the sound volume
######################################


def load_volume() -> int:
    config = mw.addonManager.getConfig(__name__)
    default_volume = 100
    if config is None:
        return default_volume

    volume = config['volume']
    if isinstance(volume, int):
        return volume

    return default_volume

def save_volume(volume: int) -> None:
    mw.addonManager.writeConfig(__name__, {'volume': volume})

    gui_hooks.av_player_did_begin_playing.remove(did_begin_playing)
    gui_hooks.av_player_did_begin_playing.append(did_begin_playing)


def set_volume(player: SimpleMplayerSlaveModePlayer, volume: int) -> None:
    player.command('volume', volume)


def did_begin_playing(player: Any, _: AVTag) -> None:
    volume = load_volume()
    # mplayer seems to lose commands sent to it immediately after startup,
    # so we add a delay for it - an alternate approach would be to adjust
    # the command line arguments passed to it
    if isinstance(player, SimpleMplayerSlaveModePlayer):
        mw.progress.timer(500, lambda: set_volume(player, volume), False)
    elif isinstance(player, MpvManager):
        player.set_property("volume", volume)


gui_hooks.av_player_did_begin_playing.append(did_begin_playing)


class VolumeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        volume = load_volume()

        slider = QSlider()
        slider.setOrientation(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(volume)

        spin_box = QSpinBox()
        spin_box.setMinimum(0)
        spin_box.setMaximum(100)
        spin_box.setValue(volume)

        slider.valueChanged.connect(spin_box.setValue)
        slider.valueChanged.connect(save_volume)

        spin_box.valueChanged.connect(slider.setValue)
        spin_box.valueChanged.connect(save_volume)

        layout = QHBoxLayout()
        layout.addWidget(slider)
        layout.addWidget(spin_box)

        self.setWindowTitle("Adjust the Volume")
        self.setLayout(layout)

volume_dialog = VolumeDialog(mw)

action = QAction('Adjust Sound Volume...')
action.triggered.connect(volume_dialog.show)
mw.form.menuTools.addAction(action)
