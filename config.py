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
Handle the volume configurations
"""
from dataclasses import dataclass
from dataclasses import field

from aqt import mw


@dataclass
class LoudnormConfig:
    """The loudnorm filter configuration"""
    enabled: bool = False
    i: int = -24


@dataclass
class VolumeConfig:
    """The volume configuration"""
    volume: int = 100
    loudnorm: LoudnormConfig = field(default_factory=LoudnormConfig)


def load_config() -> VolumeConfig:
    """Load the sound volume configuration."""
    volume_config = VolumeConfig()

    config = mw.addonManager.getConfig(__name__)
    if config is None:
        return volume_config

    if 'volume' in config and isinstance(config['volume'], int):
        volume_config.volume = config['volume']

    if 'loudnorm' in config:
        if 'enabled' in config['loudnorm'] and isinstance(config['loudnorm']['enabled'], bool):
            volume_config.loudnorm.enabled = config['loudnorm']['enabled']

        if 'i' in config['loudnorm'] and isinstance(config['loudnorm']['i'], int):
            volume_config.loudnorm.i = config['loudnorm']['i']

    return volume_config
