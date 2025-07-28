from ...modules.utils import Blueprint, idle
from ...modules.gamebanana.types import Submission, FeaturedSubmissions
from ...modules.gamebanana import Gamebanana

from ..page_bar import PageBar
from ..submission import TopSubmission, SubmissionButton

from gi.repository import Gtk, Adw, GLib


@Blueprint("home-page")
class HomePage(Adw.Bin):
    __gtype_name__ = "HomePage"

    page_bar: PageBar = Gtk.Template.Child()
    mod_carousel: Adw.Carousel = Gtk.Template.Child()
    mods: Gtk.FlowBox = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.auto_scroll_running = True
        self.last_mod = None

        Gamebanana.get_featured_submissions(self.populate)
        Gamebanana.get_top_submissions(self.populate_carousel)

        self.page_bar.set_banana_func(
            Gamebanana.get_featured_submissions, self.populate
        )

        self.start_auto_scroll()  # TODO: make this configurable

    def start_auto_scroll(self):
        controller = Gtk.GestureClick.new()
        self.add_controller(controller)
        controller.connect("released", self.stop_auto_scroll)

    def stop_auto_scroll(self, *_):
        self.auto_scroll_running = False

    def auto_scroll(self):
        if self.auto_scroll_running is False:
            return False

        if self.last_mod is None:
            self.last_mod = self.mod_carousel.get_first_child()

        if self.last_mod is None:
            return False

        self.last_mod = self.last_mod.get_next_sibling()
        if self.last_mod is None:
            self.last_mod = self.mod_carousel.get_first_child()

        self.mod_carousel.scroll_to(self.last_mod, True)
        return True

    def populate_carousel(self, submissions: list[Submission]):
        for x in submissions:
            mod = TopSubmission(x)
            idle(self.mod_carousel.append, mod)

        GLib.timeout_add_seconds(5, self.auto_scroll)

    def populate(self, submissions: FeaturedSubmissions, page: int):
        idle(self.mods.remove_all)

        meta = submissions["_aMetadata"]
        self.page_bar.update_widgets(meta, page)

        if meta["_nRecordCount"] > 0:
            for x in submissions["_aRecords"]:
                btt = SubmissionButton(x)
                idle(self.mods.append, btt)
