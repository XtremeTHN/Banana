import gi
from rich.traceback import install

install(show_locals=True)

gi.require_versions({"Adw": "1", "Gtk": "4.0"})

from gi.repository import Gtk, Adw, Gio, Gdk
from .ui.window import BananaWindow


class Application(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.Banana",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        display = Gdk.Display.get_default()

        prov = Gtk.CssProvider.new()
        prov.load_from_resource("/com/github/XtremeTHN/Banana/style.css")

        Gtk.StyleContext.add_provider_for_display(
            display, prov, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        BananaWindow(self)


def run(argv):
    Application().run()
