import gi
import sys
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
        self.win = None
        self.old_hook = sys.excepthook
        sys.excepthook = self.exception_hook

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        self.old_hook(exc_type, exc_value, exc_traceback)

        diag = Adw.AlertDialog.new(
            exc_type.__name__,
            f"{' '.join(exc_value.args)}. Report this error to the github repository",
        )

        diag.add_response("a", "Accept")

        diag.present(self.win)

    def do_activate(self):
        display = Gdk.Display.get_default()

        prov = Gtk.CssProvider.new()
        prov.load_from_resource("/com/github/XtremeTHN/Banana/style.css")

        Gtk.StyleContext.add_provider_for_display(
            display, prov, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        self.win = BananaWindow(self)


def run(argv):
    Application().run()
