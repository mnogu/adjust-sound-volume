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

from aqt import gui_hooks
from aqt import mw
from aqt.qt import QAction

from . import hook
from . import ui

gui_hooks.av_player_did_begin_playing.append(hook.did_begin_playing)

action = QAction('Adjust Sound Volume...')
action.triggered.connect(ui.VolumeDialog(mw).show)
mw.form.menuTools.addAction(action)
