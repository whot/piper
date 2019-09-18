# Copyright (C) 2017 Jente Hidskes <hjdskes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from .gi_composites import GtkTemplate
from .ratbagd import RatbagdLed

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject, Gtk  # noqa


@GtkTemplate(ui="/org/freedesktop/Piper/ui/LedDialog.ui")
class LedDialog(Gtk.Dialog):
    """A Gtk.Dialog subclass to implement the dialog that shows the
    configuration options for the LED effects."""

    __gtype_name__ = "LedDialog"

    stack = GtkTemplate.Child()
    colorchooser = GtkTemplate.Child()
    colorbutton = GtkTemplate.Child()
    adjustment_brightness = GtkTemplate.Child()
    adjustment_effect_duration = GtkTemplate.Child()
    led_off_image = GtkTemplate.Child()

    def __init__(self, ratbagd_led, *args, **kwargs):
        """Instantiates a new LedDialog.

        @param ratbagd_led The LED to configure, as ratbagd.RatbagdLed.
        """
        Gtk.Dialog.__init__(self, *args, **kwargs)
        self.init_template()
        self._led = ratbagd_led
        self._modes = {
            "solid": RatbagdLed.Mode.ON,
            "cycle": RatbagdLed.Mode.CYCLE,
            "breathing": RatbagdLed.Mode.BREATHING,
            "off": RatbagdLed.Mode.OFF
        }

        mode = self._led.mode
        for k, v in self._modes.items():
            if mode == v:
                self.stack.set_visible_child_name(k)
            if v not in self._led.modes:
                self.stack.get_child_by_name(k).set_visible(False)
        rgba = self._get_led_color_as_rgba()
        self.colorchooser.set_rgba(rgba)
        self.colorbutton.set_rgba(rgba)
        self.adjustment_brightness.set_value(self._led.brightness)
        self.adjustment_effect_duration.set_value(self._led.effect_duration)

        sp = Gtk.CssProvider()
        sp.load_from_data("* { background: #565854}".encode())
        Gtk.StyleContext.add_provider(self.led_off_image.get_style_context(),
                                      sp, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @GtkTemplate.Callback
    def _on_change_value(self, scale, scroll, value):
        # Round the value resulting from a scroll event to the nearest multiple
        # of 500. This is to work around the Gtk.Scale not snapping to its
        # Gtk.Adjustment's step_increment.
        scale.set_value(int(value - (value % 500)))
        return True

    def _get_led_color_as_rgba(self):
        # Helper function to convert ratbagd's 0-255 color range to a Gdk.RGBA
        # with a 0.0-1.0 color range.
        r, g, b = self._led.color
        return Gdk.RGBA(r / 255.0, g / 255.0, b / 255.0, 1.0)

    @GObject.Property
    def mode(self):
        visible_child = self.stack.get_visible_child_name()
        return self._modes[visible_child]

    @GObject.Property
    def color(self):
        if self.mode == RatbagdLed.Mode.ON:
            rgba = self.colorchooser.get_rgba()
        else:
            rgba = self.colorbutton.get_rgba()
        return (rgba.red * 255.0, rgba.green * 255.0, rgba.blue * 255.0)

    @GObject.Property
    def brightness(self):
        return self.adjustment_brightness.get_value()

    @GObject.Property
    def effect_duration(self):
        return self.adjustment_effect_duration.get_value()
