from gi.repository import Gtk, Adw

from banana.modules.utils import Blueprint, idle

from . import SubmissionPage, HtmlView


@Blueprint("wip-page")
class WipPage(Adw.NavigationPage, SubmissionPage):
    __gtype_name__ = "WipPage"

    submission_icon: Gtk.Picture = Gtk.Template.Child()
    submission_title: Gtk.Label = Gtk.Template.Child()
    submission_caption: Gtk.Label = Gtk.Template.Child()
    submission_description: HtmlView = Gtk.Template.Child()

    completed: Gtk.LevelBar = Gtk.Template.Child()
    completed_label: Gtk.Label = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()

    submission_updates_box: Gtk.ListBox = Gtk.Template.Child()
    submission_credits_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    submission_type = "Wip"

    def __init__(self, submission_id):
        Adw.NavigationPage.__init__(self, title=" - Work in progress")
        SubmissionPage.__init__(self, submission_id)

        self.request_info()

    def populate_extra_widgets(self, submission):
        idle(
            self.completed_label.set_label,
            f"{submission['_sDevelopmentState']} - {submission['_iCompletionPercentage']}% completed",
        )
        idle(self.completed.set_value, submission["_iCompletionPercentage"] / 100)
