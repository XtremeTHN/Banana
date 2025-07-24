from ..modules.utils import Blueprint

# from .sidebar import BananaSidebar
from .nav import Navigation
from .home import HomePage
from .search import SearchPage

from gi.repository import Gtk, Adw


@Blueprint("window")
class BananaWindow(Adw.ApplicationWindow):
    __gtype_name__ = "BananaWindow"

    stack: Gtk.Stack = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    nav_view: Navigation = Gtk.Template.Child()

    home_page: HomePage = Gtk.Template.Child()
    search_page: SearchPage = Gtk.Template.Child()

    def __init__(self, app):
        super().__init__(application=app)
        Navigation._instance = self.nav_view

        self.search_bar.set_key_capture_widget(self)
        self.present()

    @classmethod
    def get_default(cls):
        return cls._instance

    @Gtk.Template.Callback()
    def on_search_changed(self, entry: Gtk.SearchEntry):
        if entry.get_text() == "":
            self.stack.set_visible_child_name("home")
            return

        self.stack.set_visible_child_name("home-search")

    @Gtk.Template.Callback()
    def on_serch_btt_clicked(self, btt):
        self.search_bar.set_search_mode(not self.search_bar.props.search_mode_enabled)
