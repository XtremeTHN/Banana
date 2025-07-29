from gi.repository import Gtk, Adw

from banana.modules.utils import Blueprint
from .download import SubmissionDownloadDialog
from banana.modules.gamebanana import Gamebanana
from . import SubmissionPage


@Blueprint("mod-page")
class ModPage(Adw.NavigationPage, SubmissionPage):
    __gtype_name__ = "ModPage"

    submission_icon: Gtk.Picture = Gtk.Template.Child()
    submission_title: Gtk.Label = Gtk.Template.Child()
    submission_caption: Gtk.Label = Gtk.Template.Child()
    submission_description: Gtk.TextView = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()
    submission_credits_box: Gtk.ListBox = Gtk.Template.Child()
    submission_updates_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    downloads: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    submission_type = "Mod"

    def __init__(self, mod_id: int):
        Adw.NavigationPage.__init__(self, title="Mod")
        SubmissionPage.__init__(self, mod_id)

        self.request_info()

    @Gtk.Template.Callback()
    def on_download_clicked(self, _):
        diag = SubmissionDownloadDialog(
            self.info["_sName"],
            self.info.get("_aFiles", []),
            self.info.get("_aAlternateFileSources", []),
        )
        diag.present(self.get_root())
