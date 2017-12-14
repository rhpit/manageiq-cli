# Copyright (C) 2017 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


class Collection(object):
    """
    Collection Class

    Main option is to save the settings
    """

    _settings = None

    def __init__(self, settings):
        """
        :param settings: MIQ settings
        :type settings: dict
        """
        self._settings = settings

    @property
    def settings(self):
        """
        :return: dict of settings
        """
        return self._settings
