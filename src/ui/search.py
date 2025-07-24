from ..modules.utils import Blueprint
from gi.repository import Gtk, Adw


@Blueprint("search-page")
class SearchPage(Adw.Bin):
    __gtype_name__ = "SearchPage"

    mods: Gtk.FlowBox = Gtk.Template.Child()

    search_bar: Gtk.SearchBar = None

    def __init__(self): ...
