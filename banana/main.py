import gi
import sys
import logging
import threading
from rich.logging import RichHandler
from rich.traceback import install

install(show_locals=True)
gi.require_versions({"Adw": "1", "Gtk": "4.0"})
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

from .modules.utils import idle
from .ui.window import BananaWindow

# TODO: add a logger with rich


class Application(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.XtremeTHN.Banana",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.win = None
        self.old_hook = sys.excepthook
        self.logger = logging.getLogger("Application")

        sys.excepthook = self.exception_hook
        threading.excepthook = self.exception_hook

        self.__register_args()

    def exception_hook(self, exc_type, *extra):
        if len(extra) > 0:
            exc_value = extra[0]
            exc_traceback = extra[1]
        else:
            exc_value = exc_type.exc_value
            exc_traceback = exc_type.exc_traceback
            exc_type = exc_type.exc_type

        self.old_hook(exc_type, exc_value, exc_traceback)
        try:
            self.present_err_diag(exc_type.__name__, " ".join(exc_value.args))
        except Exception:
            self.logger.exception("Error while trying to show exception in the window")

    def present_err_diag(self, title, body):
        diag = Adw.AlertDialog.new(
            title,
            f"{body}.\nReport this error to the github repository",
        )

        diag.add_response("a", "Accept")

        idle(diag.present, self.win)

    def __register_args(self):
        self.add_main_option(
            "log-level",
            ord("l"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "The log level",
        )

    def do_command_line(self, command_line):
        cmd = command_line.get_options_dict()

        levels = logging.getLevelNamesMapping()
        log_level = "INFO"

        if cmd.contains("log-level"):
            log_level = levels.get(cmd.lookup_value("log-level").get_string().upper())

            if log_level is None:
                print("Invalid log level. Valid log levels are:", levels)
                return 1

        logging.basicConfig(
            level=log_level,
            format="[%(name)s] [%(funcName)s] %(message)s",
            handlers=[
                RichHandler(rich_tracebacks=True),
            ],
        )

        self.do_activate()
        return 0

    def do_activate(self):
        Adw.Application.do_activate(self)
        display = Gdk.Display.get_default()

        prov = Gtk.CssProvider.new()
        prov.load_from_resource("/com/github/XtremeTHN/Banana/style.css")

        Gtk.StyleContext.add_provider_for_display(
            display, prov, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        self.win = self.props.active_window
        if not self.win:
            self.win = BananaWindow(self)


def run(argv):
    Application().run(argv)
