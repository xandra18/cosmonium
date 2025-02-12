#
#This file is part of Cosmonium.
#
#Copyright (C) 2018-2019 Laurent Deru.
#
#Cosmonium is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Cosmonium is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Cosmonium.  If not, see <https://www.gnu.org/licenses/>.
#

from __future__ import print_function
from __future__ import absolute_import

from panda3d.core import LVector3d, LQuaterniond

from .frame import J2000EquatorialReferenceFrame
from . import units

from math import pow, log, log10, exp, sqrt, asin, pi

# Brightness increase factor for one magnitude
magnitude_brightness_ratio = pow(10.0, 0.4)

#Factor to convert luminosity to magnitude
luminosity_magnitude_factor = log(10.0) / 2.5

#Ang diameter to arcseconds
ang_diameter_to_arcsec = 3600 * 180 / pi

# m = M + 5 * (log10(d) - 1)
def abs_to_app_mag(abs_magnitude, distance):
    app_magnitude = abs_magnitude + 5 * (log10(distance / units.KmPerParsec) - 1)
    return app_magnitude

# M = m - 5 * (log10(d) - 1)
def app_to_abs_mag(app_magnitude, distance):
    abs_magnitude = app_magnitude - 5 * (log10(distance / units.KmPerParsec) - 1)
    return abs_magnitude

# L* = L0 * 10^((M0 - M*) / 2.5)
def abs_mag_to_lum(abs_magnitude):
    return exp((units.sun_abs_magnitude - abs_magnitude) * luminosity_magnitude_factor)

# M* = M0 - 2.5 * log10(L* / L0)
def lum_to_abs_mag(luminosity):
    return units.sun_abs_magnitude - log(luminosity) / luminosity_magnitude_factor

def mag_to_surface_brightness(mag, distance, radius):
    if radius < distance:
        arc_radius = asin(radius / distance) * ang_diameter_to_arcsec
    else:
        arc_radius = 3600 * 180
    arc_surface = pi * arc_radius * arc_radius
    return  mag + 2.5 * log(arc_surface)

# L*/L0 = (R*/R0)^2 * (T*/T0)^4
# R* = (T*/T0)^2 * (L*/L0)^0.5 * R0
def temp_to_radius(temperature, abs_magnitude):
    temperature_ratio = units.sun_temperature / temperature
    luminosity_ratio = pow(magnitude_brightness_ratio, units.sun_abs_magnitude - abs_magnitude)
    radius = temperature_ratio * temperature_ratio * sqrt(luminosity_ratio) * units.sun_radius
    return radius

def calc_orientation_from_incl_an(inclination, ascending_node, flipped=False):
    inclination_quat = LQuaterniond()
    if flipped:
        inclination += pi
    inclination_quat.setFromAxisAngleRad(inclination, LVector3d.unitX())
    ascending_node_quat = LQuaterniond()
    ascending_node_quat.setFromAxisAngleRad(ascending_node, LVector3d.unitZ())
    return inclination_quat * ascending_node_quat

def calc_orientation(right_ascension, declination, flipped=False):
    inclination = pi / 2 - declination
    ascending_node = right_ascension + pi / 2
    orientation = calc_orientation_from_incl_an(inclination, ascending_node, flipped)
    return orientation * J2000EquatorialReferenceFrame.orientation
