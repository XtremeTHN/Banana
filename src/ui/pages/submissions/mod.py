from gi.repository import Gtk, Adw

from src.ui.screenshot import Screenshot
from src.modules.cache import cache_download
from src.modules.utils import Blueprint, idle
from .download import SubmissionDownloadDialog
from src.modules.gamebanana import Gamebanana
from src.modules.gamebanana.types import SubmissionInfo
from .utils import sanitaze_html, populate_credits, populate_updates


@Blueprint("mod-page")
class ModPage(Adw.NavigationPage):
    __gtype_name__ = "ModPage"

    mod_icon: Gtk.Picture = Gtk.Template.Child()
    mod_title: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()
    mod_description: Gtk.Label = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()
    credits_box: Gtk.ListBox = Gtk.Template.Child()
    updates_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    downloads: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, mod_id):
        super().__init__(title="Mod")

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

        self.mod_id = mod_id
        self.info: SubmissionInfo = None

        # TODO: if this converts into a gamebanana general client, change this to the type of the submission id
        Gamebanana.get_submission_info("Mod", mod_id, self.populate)

    @Gtk.Template.Callback()
    def on_download_clicked(self, _):
        diag = SubmissionDownloadDialog(
            self.info["_sName"],
            self.info.get("_aFiles", []),
            self.info.get("_aAlternateFileSources", []),
        )
        diag.present(self.get_root())

    def populate(self, submission: SubmissionInfo):
        def finish(cover, *images):
            idle(self.mod_icon.set_filename, cover)

            for img in images:
                s = Screenshot()
                idle(s.pic.set_filename, img)
                idle(self.screenshots_carousel.append, s)

            idle(self.mod_title.set_label, submission["_sName"])
            idle(self.mod_caption.set_label, submission["_aSubmitter"]["_sName"])

            idle(self.likes.set_label, f"{submission['_nLikeCount']:,}")
            idle(self.views.set_label, f"{submission['_nViewCount']:,}")
            idle(self.downloads.set_label, f"{submission['_nDownloadCount']:,}")

            idle(self.mod_description.set_label, sanitaze_html(submission["_sText"]))

            populate_updates(self.updates_box, "Mod", self.mod_id)
            populate_credits(self.credits_box, submission["_aCredits"])

            idle(self.stack.set_visible_child_name, "main")

        self.set_title(submission["_sName"] + " - Mod")

        if submission["_bIsTrashed"]:
            self.stack.set_visible_child_name("trashed")
            self.trashed_status.set_description(
                f"This submission was trashed: {submission['_aTrashInfo']['_sReason']}"
            )
            return

        self.info = submission
        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
