import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio
import workbench


cover = Gio.File.new_for_path("/home/axel/Pictures/preview1.jpg")
mod_prev = workbench.builder.get_object("mod_preview")
mod_prev.props.file = cover
