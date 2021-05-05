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
Test the behavior in loading configurations
"""
import unittest
from typing import Dict
from typing import Union
from unittest.mock import patch

from config import load_config
from config import LoudnormConfig
from config import VolumeConfig


class TestConfig(unittest.TestCase):
    """A class to test the loading of configurations"""

    def setUp(self) -> None:
        self.patcher = patch('config.mw')
        self.mock = self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

    def _get_config(self, config: Union[Dict, None]) -> VolumeConfig:
        self.mock.addonManager.getConfig.return_value = config
        return load_config()

    def test_default(self) -> None:
        """Validate the default value."""
        actual = self._get_config({
            'volume': 100
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_none(self) -> None:
        """Test with None value."""
        actual = self._get_config(None)
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_empty(self) -> None:
        """Test with an empty value."""
        actual = self._get_config({})
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_valid_volume(self) -> None:
        """Test with a valid volume value."""
        actual = self._get_config({
            'volume': 70
        })
        expected = VolumeConfig(
            volume=70,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_invalid_volume(self) -> None:
        """Test with an invalid volume value."""
        actual = self._get_config({
            'volume': 'a'
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_valid_loudnorm(self) -> None:
        """Test with loudnorm enabled."""
        actual = self._get_config({
            'volume': 100,
            'loudnorm': {
                'enabled': True
            }
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=True,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_invalid_loudnorm(self) -> None:
        """Test with an invalid loudnorm configuration."""
        actual = self._get_config({
            'volume': 100,
            'loudnorm': {
                'enabled': 7
            }
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=False,
                i=-24
            )
        )
        self.assertEqual(actual, expected)

    def test_valid_loudnorm_i(self) -> None:
        """Test with a valid integrated loudness value."""
        actual = self._get_config({
            'volume': 100,
            'loudnorm': {
                'enabled': True,
                'i': -12
            }
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=True,
                i=-12
            )
        )
        self.assertEqual(actual, expected)

    def test_invalid_loudnorm_i(self) -> None:
        """Test with an invalid integrated loudness value."""
        actual = self._get_config({
            'volume': 100,
            'loudnorm': {
                'enabled': True,
                'i': 'a'
            }
        })
        expected = VolumeConfig(
            volume=100,
            loudnorm=LoudnormConfig(
                enabled=True,
                i=-24
            )
        )
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
