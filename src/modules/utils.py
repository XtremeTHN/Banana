import threading as t
from gi.repository import Gtk, GLib


def idle(func, *args):
    return GLib.idle_add(func, *args)


def idle_wrap(func):
    def wrapper(*args):
        idle(func, *args)

    return wrapper


class Blueprint(Gtk.Template):
    def __init__(self, blp_name):
        super().__init__(resource_path=f"/com/github/XtremeTHN/Banana/{blp_name}.ui")


class Thread(t.Thread):
    def __init__(self, func, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.func = func
        super().__init__()

    def run(self):
        self.func(*self.args, **self.kwargs)

    def __call__(self, *args, **kwds):
        self.args = args
        self.kwargs = kwds
        self.start()
