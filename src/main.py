import gi
import sys
import threading
from rich.traceback import install

install(show_locals=True)
gi.require_versions({"Adw": "1", "Gtk": "4.0"})
from gi.repository import Gtk, Adw, Gio, Gdk

from .modules.utils import idle
from .ui.window import BananaWindow


class Application(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.Banana",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.win = None
        self.old_thread_hook = threading.excepthook
        self.old_hook = sys.excepthook

        sys.excepthook = self.exception_hook
        threading.excepthook = self.thread_hook

    def thread_hook(self, args: threading.ExceptHookArgs):
        self.old_thread_hook(args)
        self.present_err_diag(args.exc_type.__name__, " ".join(args.exc_value.args))

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        self.old_hook(exc_type, exc_value, exc_traceback)
        self.present_err_diag(exc_type.__name__, " ".join(exc_value.args))

    def present_err_diag(self, title, body):
        diag = Adw.AlertDialog.new(
            title,
            f"{body}.\nReport this error to the github repository",
        )

        diag.add_response("a", "Accept")

        idle(diag.present, self.win)

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
