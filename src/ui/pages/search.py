from ...modules.utils import Blueprint, idle
from ...modules.gamebanana import Gamebanana
from ...modules.gamebanana.types import QuerySubmission, PagedResponse

from ..page_bar import PageBar
from ..mod import ModButton
from gi.repository import Gtk, Adw, GLib, GObject


@Blueprint("search-page")
class SearchPage(Adw.Bin):
    __gtype_name__ = "SearchPage"

    page_bar: PageBar = Gtk.Template.Child()
    mods: Gtk.FlowBox = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()

    loading_page: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.__search_entry = None
        self.page_bar.set_banana_func(self.__request_page, self.__handle_query)

        spinner = Adw.SpinnerPaintable.new()
        spinner.set_widget(self.loading_page)
        self.loading_page.set_paintable(spinner)

    def __request_page(self, cb, page):
        Gamebanana.query_submissions(self.search_entry.get_text(), cb, page=page)

    @GObject.Property(nick="search-entry", type=Gtk.Widget)
    def search_entry(self):
        return self.__search_entry

    @search_entry.setter
    def search_entry(self, entry):
        print("setted")
        self.__search_entry = entry
        entry.connect("search-changed", self.search)

    def populate(self, submissions: list[QuerySubmission]):
        GLib.idle_add(self.mods.remove_all)
        idle(self.stack.set_visible_child_name, "results")

        for x in submissions:
            m = ModButton(x)
            GLib.idle_add(self.mods.append, m)

    def __handle_query(self, submissions: PagedResponse, page: int):
        meta = submissions["_aMetadata"]
        self.page_bar.update_widgets(meta, page)

        if meta["_nRecordCount"] > 0:
            self.populate(submissions["_aRecords"])
        else:
            idle(self.stack.set_visible_child_name, "no-results")
            return

    def search(self, entry: Gtk.SearchEntry):
        self.stack.set_visible_child_name("loading")
        self.mods.remove_all()

        query = entry.get_text().strip()

        if len(query) < 3:
            self.stack.set_visible_child_name("too-short")
            return

        Gamebanana.query_submissions(query, self.__handle_query)
