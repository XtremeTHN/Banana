from ..modules.utils import Blueprint
from gi.repository import Gtk


@Blueprint("screenshot")
class Screenshot(Gtk.Box):
    __gtype_name__ = "Screenshot"

    pic: Gtk.Picture = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
