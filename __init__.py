# -*- coding: utf-8 -*-
# Copyright: Muneyuki Noguchi
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Adjust the sound volume in 2.1.x.
"""

from typing import Any

from aqt.qt import QAction
from aqt.qt import QDialog
from aqt.qt import QDialogButtonBox
from aqt.qt import QHBoxLayout
from aqt.qt import QSlider
from aqt.qt import QSpinBox
from aqt.qt import QVBoxLayout
from aqt.qt import QWidget
from aqt.qt import Qt
from aqt.sound import MpvManager
from aqt.sound import SimpleMplayerSlaveModePlayer
from aqt import gui_hooks
from aqt import mw
from anki.sound import AVTag

# Adjust the sound volume
######################################


def load_volume() -> int:
    """Load the sound volume configuration."""
    config = mw.addonManager.getConfig(__name__)
    default_volume = 100
    if config is None:
        return default_volume

    volume = config['volume']
    if isinstance(volume, int):
        return volume

    return default_volume


def save_volume(volume: int) -> None:
    """Save the sound volume configuration."""
    mw.addonManager.writeConfig(__name__, {'volume': volume})

    gui_hooks.av_player_did_begin_playing.remove(did_begin_playing)
    gui_hooks.av_player_did_begin_playing.append(did_begin_playing)


def did_begin_playing(player: Any, _: AVTag) -> None:
    """Set the sound volume."""
    volume = load_volume()
    if isinstance(player, SimpleMplayerSlaveModePlayer):
        player.command('volume', volume, '1')
    elif isinstance(player, MpvManager):
        player.set_property('volume', volume)


gui_hooks.av_player_did_begin_playing.append(did_begin_playing)


class VolumeDialog(QDialog):
    """A dialog window to set the sound volume"""
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)

        self.spin_box = QSpinBox()
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(100)

        self.slider.valueChanged.connect(self.spin_box.setValue)
        self.spin_box.valueChanged.connect(self.slider.setValue)

        h_box_layout = QHBoxLayout()
        h_box_layout.addWidget(self.slider)
        h_box_layout.addWidget(self.spin_box)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        v_box_layout = QVBoxLayout()
        v_box_layout.addLayout(h_box_layout)
        v_box_layout.addWidget(button_box)

        self.setModal(True)
        self.setWindowTitle('Adjust the Volume')
        self.setLayout(v_box_layout)

    def show(self) -> None:
        """Show the dialog window and its widgets."""
        volume = load_volume()
        self.slider.setValue(volume)
        self.spin_box.setValue(volume)
        super().show()

    def accept(self) -> None:
        """Save the sound volume and hide the dialog window."""
        save_volume(self.slider.value())
        super().accept()


action = QAction('Adjust Sound Volume...')
action.triggered.connect(VolumeDialog(mw).show)
mw.form.menuTools.addAction(action)
