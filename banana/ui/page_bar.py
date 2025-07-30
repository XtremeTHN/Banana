from ..modules.utils import Blueprint, idle
from ..modules.gamebanana.types import PagedRespondeMetadata

from gi.repository import Gtk
import logging


@Blueprint("page-bar")
class PageBar(Gtk.CenterBox):
    __gtype_name__ = "PageBar"

    prev_btt: Gtk.Button = Gtk.Template.Child()
    page_counter: Gtk.Label = Gtk.Template.Child()
    next_btt: Gtk.Button = Gtk.Template.Child()

    sort_type_dropdown: Gtk.DropDown = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.func_cb = None
        self.func = None
        self.current_page = 1
        self.logger = logging.getLogger("PageBar")

        self.sort_type_dropdown.connect("notify::selected-item", self.__on_sort_changed)

    def __on_sort_changed(self, *_):
        self.func(
            self.func_cb,
            sort=self.sort_type_dropdown.get_selected_item().get_string().lower(),
            page=self.current_page,
        )

    def set_page(self, page):
        self.page_counter.set_label(page)
        try:
            self.current_page = int(page)
        except ValueError:
            self.logger.warning("Invalid page number:", page)
            self.current_page = 1

    def disable(self):
        idle(self.next_btt.set_sensitive, False)
        idle(self.prev_btt.set_sensitive, False)

    def update_widgets(self, metadata: PagedRespondeMetadata, page: int):
        # if _bIsComplete is false, then more pages are available.
        idle(self.next_btt.set_sensitive, not metadata["_bIsComplete"])
        idle(self.prev_btt.set_sensitive, page > 1)
        idle(self.page_counter.set_label, str(page))

        self.current_page = page

    def set_banana_func(self, gamebanana_func, func_cb):
        self.func_cb = func_cb
        self.func = gamebanana_func

    @Gtk.Template.Callback()
    def previous_page(self, _):
        self.func(self.func_cb, page=self.current_page - 1)

    @Gtk.Template.Callback()
    def next_page(self, _):
        self.func(self.func_cb, page=self.current_page + 1)
