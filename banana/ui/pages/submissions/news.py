from . import SubmissionPage, SubmissionInfo
from banana.modules.utils import Blueprint
from gi.repository import Gtk, Adw
from .html import HtmlView


@Blueprint("news-page")
class NewsPage(Adw.NavigationPage, SubmissionPage):
    __gtype_name__ = "NewsPage"
    submission_icon: Gtk.Picture = Gtk.Template.Child()
    submission_title: Gtk.Label = Gtk.Template.Child()
    submission_caption: Gtk.Label = Gtk.Template.Child()
    submission_description: HtmlView = Gtk.Template.Child()

    stack: Gtk.Stack = Gtk.Template.Child()
    screenshots_carousel: Adw.Carousel = Gtk.Template.Child()

    submission_updates_box: Gtk.ListBox = Gtk.Template.Child()

    likes: Gtk.Label = Gtk.Template.Child()
    views: Gtk.Label = Gtk.Template.Child()

    loading_status: Adw.StatusPage = Gtk.Template.Child()
    trashed_status: Adw.StatusPage = Gtk.Template.Child()

    submission_type = "News"

    def __init__(self, submission_id: int):
        Adw.NavigationPage.__init__(self)
        SubmissionPage.__init__(self, submission_id)

        self.request_info()
