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
Defines the sound configuration UI.
"""
from dataclasses import asdict
from typing import Tuple

from aqt import gui_hooks
from aqt import mw
from aqt.qt import QCheckBox
from aqt.qt import QDialog
from aqt.qt import QDialogButtonBox
from aqt.qt import QGridLayout
from aqt.qt import QGroupBox
from aqt.qt import QHBoxLayout
from aqt.qt import QLabel
from aqt.qt import QListView
from aqt.qt import QMessageBox
from aqt.qt import QPushButton
from aqt.qt import QSize
from aqt.qt import QSizePolicy
from aqt.qt import QSlider
from aqt.qt import QSpinBox
from aqt.qt import QStringListModel
from aqt.qt import QVBoxLayout
from aqt.qt import QWidget
from aqt.qt import Qt
from aqt.sound import MpvManager
from aqt.sound import av_player

from . import config
from . import hook


def save_config(volume_config: config.VolumeConfig) -> None:
    """Save the sound volume configuration."""
    mw.addonManager.writeConfig(__name__, asdict(volume_config))

    gui_hooks.av_player_did_begin_playing.remove(hook.did_begin_playing)
    gui_hooks.av_player_did_begin_playing.append(hook.did_begin_playing)


def _create_config_widgets(text: str, min_max: Tuple[int, int]) \
        -> Tuple[QLabel, QSlider, QSpinBox]:
    label = QLabel()
    label.setText(text)
    label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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


class FileListView(QListView):
    """A file name list view with the size hint"""

    # pylint: disable=C0103
    def sizeHint(self) -> QSize:
        """Return the size hint."""
        # make the height smaller
        return QSize(self.sizeHintForColumn(0), self.sizeHintForRow(0) * 3)


class FileListLayout(QHBoxLayout):
    """A file name list layout"""

    def __init__(self) -> None:
        super().__init__()

        model = QStringListModel()

        view = FileListView()
        view.setModel(model)

        button_to_add = QPushButton()
        button_to_add.setText('Add')

        button_to_remove = QPushButton()
        button_to_remove.setText('Remove')

        layout = QVBoxLayout()
        layout.addWidget(button_to_add)
        layout.addWidget(button_to_remove)
        layout.addStretch()

        self.addWidget(view)
        self.addLayout(layout)


class VolumeDialog(QDialog):
    """A dialog window to set the sound volume"""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        volume_label, self.volume_slider, self.volume_spin_box = _create_config_widgets(
            'Volume', (0, 100))

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_spin_box)

        volume_group_box = QGroupBox()
        volume_group_box.setLayout(volume_layout)
        volume_group_box.setTitle('General')

        i_label, self.i_slider, self.i_spin_box = _create_config_widgets(
            'Integrated loudness', (-70, -5))
        self.dual_mono_check_box = QCheckBox(
            'Treat mono input as dual-mono')

        loudnorm_layout = QGridLayout()
        loudnorm_layout.addWidget(i_label, 0, 0)
        loudnorm_layout.addWidget(self.i_slider, 0, 1)
        loudnorm_layout.addWidget(self.i_spin_box, 0, 2)
        loudnorm_layout.addWidget(self.dual_mono_check_box, 1, 0, 1, 3)

        self.loudnorm_group_box = QGroupBox()
        self.loudnorm_group_box.setLayout(loudnorm_layout)
        self.loudnorm_group_box.setCheckable(True)
        self.loudnorm_group_box.setTitle(
            'Loudness Normalization (mpv only)')
        self.loudnorm_group_box.toggled.connect(self._show_warning_on_non_mpv)

        file_group_box = QGroupBox()
        file_group_box.setLayout(FileListLayout())
        file_group_box.setTitle('Files not to adjust')

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(volume_group_box)
        layout.addWidget(self.loudnorm_group_box)
        layout.addWidget(file_group_box)
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

        self.loudnorm_group_box.setChecked(loudnorm.enabled)

        _set_value(loudnorm.i, self.i_slider, self.i_spin_box)
        self.dual_mono_check_box.setChecked(loudnorm.dual_mono)

        super().show()

    def accept(self) -> None:
        """Save the sound volume and hide the dialog window."""
        volume_config = config.VolumeConfig()
        volume_config.volume = self.volume_slider.value()
        volume_config.loudnorm.enabled = self.loudnorm_group_box.isChecked()
        volume_config.loudnorm.i = self.i_slider.value()
        volume_config.loudnorm.dual_mono = self.dual_mono_check_box.isChecked()

        save_config(volume_config)
        super().accept()
