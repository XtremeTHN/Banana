from gi.repository import Gtk, Adw

from banana.ui.screenshot import Screenshot
from banana.modules.utils import Blueprint, idle
from banana.modules.cache import cache_download
from banana.modules.gamebanana import Gamebanana
from banana.modules.gamebanana.types import SubmissionWip
from .utils import populate_credits, populate_updates, parse


@Blueprint("wip-page")
class WipPage(Adw.NavigationPage):
    __gtype_name__ = "WipPage"

    wip_icon: Gtk.Picture = Gtk.Template.Child()
    wip_title: Gtk.Label = Gtk.Template.Child()
    wip_caption: Gtk.Label = Gtk.Template.Child()
    wip_description: Gtk.TextView = Gtk.Template.Child()
    wip_desc_buffer: Gtk.TextBuffer = Gtk.Template.Child()

    completed: Gtk.LevelBar = Gtk.Template.Child()
    completed_label: Gtk.Label = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()

    updates_box: Gtk.ListBox = Gtk.Template.Child()
    credits_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    def __init__(self, mod_id):
        super().__init__(title=" - Work in progress")

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

        self.wip_id = mod_id

        # TODO: if this converts into a gamebanana general client, change this to the type of the submission id
        Gamebanana.get_submission_info("Wip", mod_id, self.populate)

    def populate(self, submission: SubmissionWip):
        def finish(cover, *images):
            idle(self.wip_icon.set_filename, cover)

            for img in images:
                s = Screenshot()
                idle(s.pic.set_filename, img)
                idle(self.screenshots_carousel.append, s)

            idle(self.wip_title.set_label, submission["_sName"])
            idle(self.wip_caption.set_label, submission["_aSubmitter"]["_sName"])

            idle(self.likes.set_label, f"{submission['_nLikeCount']:,}")
            idle(self.views.set_label, f"{submission['_nViewCount']:,}")

            # idle(self.wip_description.set_label, sanitaze_html(submission["_sText"]))

            idle(
                self.completed_label.set_label,
                f"{submission['_sDevelopmentState']} - {submission['_iCompletionPercentage']}% completed",
            )
            idle(self.completed.set_value, submission["_iCompletionPercentage"] / 100)

            populate_updates(self.updates_box, "Wip", self.wip_id)
            populate_credits(self.credits_box, submission["_aCredits"])

            parse(submission["_sText"], self.wip_desc_buffer)
            idle(self.stack.set_visible_child_name, "main")

        self.set_title(submission["_sName"] + " - Work in progress")
        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
