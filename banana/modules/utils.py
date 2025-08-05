import re
import threading as t
from gi.repository import Gtk, GLib, GObject


def idle(func, *args):
    return GLib.idle_add(func, *args)


def idle_wrap(func):
    def wrapper(*args):
        idle(func, *args)

    return wrapper


def remove_html_tags(html: str) -> str:
    # Replace <br> and <p> with newlines
    html = re.sub(r"<br\s*/?>", "\n", html)
    html = re.sub(r"</p>", "", html)
    html = re.sub(r"<p>", "", html)

    # Remove all other tags (or handle as needed)
    html = re.sub(r"<.*?>", "", html)

    return html.replace("&nbsp;", "").replace("&", "&amp;").strip()


class List(GObject.Object):
    def __init__(self):
        super().__init__()
        self.__items = []

    @GObject.Property
    def items(self):
        return self.__items

    def append(self, item):
        self.__items.append(item)
        self.notify("items")

    def remove(self, item):
        self.__items.remove(item)
        self.notify("items")


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
