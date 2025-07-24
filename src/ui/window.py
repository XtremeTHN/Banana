from ..modules.utils import Blueprint

# from .sidebar import BananaSidebar
from .home import HomePage
from .search import SearchPage

from gi.repository import Gtk, Adw


@Blueprint("window")
class BananaWindow(Adw.ApplicationWindow):
    __gtype_name__ = "BananaWindow"

    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    nav_view: Adw.NavigationView = Gtk.Template.Child()

    def __init__(self, app):
        super().__init__(application=app)

        self.search_bar.set_key_capture_widget(self)
        self.present()

    @Gtk.Template.Callback()
    def on_search_changed(self, entry): ...

    @Gtk.Template.Callback()
    def on_serch_btt_clicked(self, btt):
        self.search_bar.set_search_mode(not self.search_bar.props.search_mode_enabled)
