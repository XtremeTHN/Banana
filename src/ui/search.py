from ..modules.utils import Blueprint, idle
from ..modules.gamebanana import Gamebanana
from ..modules.gamebanana.types import QuerySubmission

from .mod import ModButton
from gi.repository import Gtk, Adw, GLib, GObject


@Blueprint("search-page")
class SearchPage(Adw.Bin):
    __gtype_name__ = "SearchPage"

    mods: Gtk.FlowBox = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()

    page_counter: Gtk.Label = Gtk.Template.Child()

    prev_btt: Gtk.Button = Gtk.Template.Child()
    next_btt: Gtk.Button = Gtk.Template.Child()

    current_page = GObject.Property(nick="current-page", type=int)

    def __init__(self):
        super().__init__()
        self.__search_entry = None
        # self.search_entry.connect("search-changed", self.search)
        self.page_counter.bind_property(
            "label",
            self,
            "current-page",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=self.tm,
        )

    @GObject.Property(nick="search-entry", type=Gtk.Widget)
    def search_entry(self):
        return self.__search_entry

    @search_entry.setter
    def search_entry(self, entry):
        print("setted")
        self.__search_entry = entry
        entry.connect("search-changed", self.search)

    def tm(self, _, x):
        try:
            return int(x)
        except ValueError:
            return 1

    def populate(self, submissions: list[QuerySubmission]):
        GLib.idle_add(self.mods.remove_all)

        if len(submissions) == 0:
            idle(self.stack.set_visible_child_name, "no-results")
            return

        idle(self.stack.set_visible_child_name, "results")

        for x in submissions:
            m = ModButton(x)
            GLib.idle_add(self.mods.append, m)

    def __handle_query(self, result: dict, page: int):
        # if _bIsComplete is false, then more pages are available.
        idle(self.next_btt.set_sensitive, not result["_aMetadata"]["_bIsComplete"])

        idle(self.prev_btt.set_sensitive, page > 1)

        idle(self.page_counter.set_label, str(page))

        if (n := result.get("_aRecords")) is None:
            print(n)
        else:
            self.populate(n)

    @Gtk.Template.Callback()
    def previous_page(self, _):
        Gamebanana.query_submissions(
            self.search_entry.get_text(),
            self.__handle_query,
            page=self.current_page - 1,
        )

    @Gtk.Template.Callback()
    def next_page(self, _):
        Gamebanana.query_submissions(
            self.search_entry.get_text(),
            self.__handle_query,
            page=self.current_page + 1,
        )

    def search(self, entry: Gtk.SearchEntry):
        GLib.idle_add(self.mods.remove_all)
        query = entry.get_text()

        if len(query) < 3:
            self.stack.set_visible_child_name("too-short")
            return

        Gamebanana.query_submissions(query, self.__handle_query)
