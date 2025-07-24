import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, Gio
import workbench


cover = Gio.File.new_for_path("/home/axel/Pictures/preview2.jpg")
mod_prev = workbench.builder.get_object("mod_icon")
mod_prev.props.file = cover


prev1 = Gio.File.new_for_path(
    "/home/axel/Projects/Banana/mockup/mod_page/images/carousel_prev1.jpg"
)
pic_prev1 = Gtk.Picture(file=prev1, content_fit=Gtk.ContentFit.COVER)

car = workbench.builder.get_object("car")

car.append(pic_prev1)
car.scroll_to(pic_prev1, True)
