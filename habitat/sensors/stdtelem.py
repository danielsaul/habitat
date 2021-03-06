# Copyright 2011 (C) Adam Greig, Daniel Richman
#
# This file is part of habitat.
#
# habitat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# habitat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with habitat.  If not, see <http://www.gnu.org/licenses/>.

"""
Sensor functions for dealing with telemetry.
"""

import math
from time import strptime

__all__ = ["time", "coordinate"]


def time(data):
    """
    Parse the time, validating it and returning the standard ``HH:MM:SS``.

    Accepted formats include ``HH:MM:SS``, ``HHMMSS``, ``HH:MM`` and ``HHMM``.
    It uses strptime to ensure the values are sane.
    """

    if len(data) == 8:
        t = strptime(data, "%H:%M:%S")
    elif len(data) == 6:
        t = strptime(data, "%H%M%S")
    elif len(data) == 5:
        t = strptime(data, "%H:%M")
    elif len(data) == 4:
        t = strptime(data, "%H%M")
    else:
        raise ValueError("Invalid time value.")

    return "{0.tm_hour:02d}:{0.tm_min:02d}:{0.tm_sec:02d}".format(t)


def coordinate(config, data):
    """
    Parses ASCII latitude or longitude into a decimal-degrees float.

    Either decimal degrees or degrees with decimal minutes are accepted
    (degrees, minutes and seconds are not currently supported).

    The format is specified in ``config["format"]`` and can look like either
    ``dd.dddd`` or ``ddmm.mmmm``, with one to three leading ``d`` characters
    and one to six trailing ``d`` or ``m`` characters.
    """

    if "format" not in config:
        raise ValueError("Coordinate format missing")
    coordinate_format = config["format"]

    left, right = coordinate_format.split(".")
    if left[-1] == "d" and right[-1] == "d":
        coord = float(data)
    elif left[0] == "d" and left[-1] == "m" and right[-1] == "m":
        first, second = data.split(".")
        degrees = float(first[:-2])
        minutes = float(first[-2:] + "." + second)
        if minutes > 60.0:
            raise ValueError("Minutes component > 60.")
        m_to_d = minutes / 60.0
        degrees += math.copysign(m_to_d, degrees)
        dp = len(second) + 3 # num digits in minutes + 1
        coord = round(degrees, dp)
    else:
        raise ValueError("Invalid coordinate format")

    if 'name' in config and config['name'] == 'latitude':
        if not (-90.0 <= coord <= 90.0):
            raise ValueError("Coordinate out of range (-90 <= x <= 90)")
    else:
        if not (-180.0 <= coord <= 180.0):
            raise ValueError("Coordinate out of range (-180 <= x <= 180)")

    return coord
