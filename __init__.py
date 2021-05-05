# Anki 2.1.x add-on to adjust the sound volume
# Copyright (C) 2021  Muneyuki Noguchi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Adjust the sound volume in 2.1.x.
"""

from dataclasses import asdict
from typing import Any
from typing import Tuple

from aqt.qt import QAction
from aqt.qt import QCheckBox
from aqt.qt import QDialog
from aqt.qt import QDialogButtonBox
from aqt.qt import QGridLayout
from aqt.qt import QLabel
from aqt.qt import QMessageBox
from aqt.qt import QSlider
from aqt.qt import QSpinBox
from aqt.qt import QVBoxLayout
from aqt.qt import QWidget
from aqt.qt import Qt
from aqt.sound import av_player
from aqt.sound import MpvManager
from aqt.sound import SimpleMplayerSlaveModePlayer
from aqt import gui_hooks
from aqt import mw
from anki.sound import AVTag

# false positive for 'import-self
# https://github.com/PyCQA/pylint/issues/2617
#
# pylint: disable=W0406
from . import config


def save_config(volume_config: config.VolumeConfig) -> None:
    """Save the sound volume configuration."""
    mw.addonManager.writeConfig(__name__, asdict(volume_config))

    gui_hooks.av_player_did_begin_playing.remove(did_begin_playing)
    gui_hooks.av_player_did_begin_playing.append(did_begin_playing)


def did_begin_playing(player: Any, _: AVTag) -> None:
    """Set the sound volume."""
    volume_config = config.load_config()
    if isinstance(player, SimpleMplayerSlaveModePlayer):
        player.command('volume', volume_config.volume, '1')
    elif isinstance(player, MpvManager):
        player.set_property('volume', volume_config.volume)

        # How can we retrieve the current value of the af property?
        # "player.get_property('af')" always returns "[]"
        if volume_config.loudnorm.enabled:
            loudnorm_value = 'loudnorm=I=' + str(volume_config.loudnorm.i)
        else:
            loudnorm_value = ''
        player.set_property('af', loudnorm_value)


def _create_config_widgets(text: str, min_max: Tuple[int, int]) \
        -> Tuple[QLabel, QSlider, QSpinBox]:
    label = QLabel()
    label.setText(text)

    slider = QSlider()
    slider.setOrientation(Qt.Horizontal)
    slider.setMinimum(min_max[0])
    slider.setMaximum(min_max[1])

    spin_box = QSpinBox()
    spin_box.setMinimum(min_max[0])
    spin_box.setMaximum(min_max[1])

    slider.valueChanged.connect(spin_box.setValue)
    spin_box.valueChanged.connect(slider.setValue)

    return label, slider, spin_box


def _set_value(value: int, slider: QSlider, spin_box: QSpinBox) -> None:
    for widget in [slider, spin_box]:
        widget.setValue(value)


class VolumeDialog(QDialog):
    """A dialog window to set the sound volume"""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        volume_label, self.volume_slider, self.volume_spin_box = _create_config_widgets(
            'Volume', (0, 100))

        self.loudnorm_check_box = QCheckBox(
            'Enable loudness normalization (mpv only)')

        i_label, self.i_slider, self.i_spin_box = _create_config_widgets(
            'Integrated loudness', (-70, -5))
        for widget in [i_label, self.i_slider, self.i_spin_box]:
            self.loudnorm_check_box.toggled.connect(widget.setEnabled)
        self.loudnorm_check_box.toggled.connect(self._show_warning_on_non_mpv)

        grid_layout = QGridLayout()
        grid_layout.addWidget(volume_label, 0, 0)
        grid_layout.addWidget(self.volume_slider, 0, 1)
        grid_layout.addWidget(self.volume_spin_box, 0, 2)
        grid_layout.addWidget(self.loudnorm_check_box, 1, 0, 1, 3)
        grid_layout.addWidget(i_label, 2, 0)
        grid_layout.addWidget(self.i_slider, 2, 1)
        grid_layout.addWidget(self.i_spin_box, 2, 2)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addStretch()
        layout.addWidget(button_box)

        self.setModal(True)
        self.setWindowTitle('Adjust the Volume')
        self.setLayout(layout)

    def _show_warning_on_non_mpv(self, checked: bool) -> None:
        if not checked:
            return

        if any(isinstance(player, MpvManager) for player in av_player.players):
            return

        QMessageBox.warning(self, 'mpv not found or too old',
                            'You need to install or update mpv and restart Anki '
                            'to use the loudness normalization feature.')

    def show(self) -> None:
        """Show the dialog window and its widgets."""
        volume_config = config.load_config()

        _set_value(volume_config.volume,
                   self.volume_slider, self.volume_spin_box)

        loudnorm = volume_config.loudnorm

        enabled = loudnorm.enabled
        self.loudnorm_check_box.setChecked(enabled)
        for widget in [self.i_slider, self.i_spin_box]:
            widget.setEnabled(enabled)

        _set_value(loudnorm.i, self.i_slider, self.i_spin_box)

        super().show()

    def accept(self) -> None:
        """Save the sound volume and hide the dialog window."""
        volume_config = config.VolumeConfig()
        volume_config.volume = self.volume_slider.value()
        volume_config.loudnorm.enabled = self.loudnorm_check_box.isChecked()
        volume_config.loudnorm.i = self.i_slider.value()

        save_config(volume_config)
        super().accept()


gui_hooks.av_player_did_begin_playing.append(did_begin_playing)

action = QAction('Adjust Sound Volume...')
action.triggered.connect(VolumeDialog(mw).show)
mw.form.menuTools.addAction(action)
