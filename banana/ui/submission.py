from banana.modules.gamebanana.types import Submission, SubmissionInfo
from banana.modules.cache import cache_download
from banana.modules.utils import Blueprint, idle

from .pages.submissions.news import NewsPage
from .pages.submissions.mod import ModPage
from .pages.submissions.wip import WipPage

from .nav import Navigation
from gi.repository import Gtk
import logging


class UnsupportedSubmission(Exception):
    pass


def generic_clicked(_, obj):
    page = None
    if obj.type == "Mod":
        page = ModPage(obj.submission_id)
    elif obj.type == "Wip":
        page = WipPage(obj.submission_id)
    elif obj.type == "News":
        page = NewsPage(obj.submission_id)

    if page is None:
        raise UnsupportedSubmission(
            f'Currently "{obj.type}" submissions are not supported. Submission id: {obj.submission_id}'
        )

    Navigation().get_default().navigation.push(page)


def get_formatted_period(period: str):
    match period:
        case "today":
            return "today"
        case "week":
            return "this week"
        case "month":
            return "this month"
        case "3month":
            return "this 3 months"
        case "6month":
            return "this 6 months"
        case "year":
            return "this year"
        case "alltime":
            return "all time"
        case _:
            logging.warning("Unkown period: %s", period)
            return "Unknown"


@Blueprint("top-submission")
class TopSubmission(Gtk.Overlay):
    __gtype_name__ = "TopSubmission"
    mod_preview: Gtk.Picture = Gtk.Template.Child()
    mod_feature_type: Gtk.Label = Gtk.Template.Child()
    mod_submitter: Gtk.Image = Gtk.Template.Child()

    mod_name: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()

    download_btt: Gtk.Button = Gtk.Template.Child()

    def __init__(self, submission: Submission):
        super().__init__()
        self.submission_id = submission["_idRow"]
        self.type = submission["_sModelName"]

        event = Gtk.EventControllerMotion.new()
        self.add_controller(event)
        event.connect("enter", self.__on_hover)
        event.connect("leave", self.__on_hover_lost)

        self.download_btt.connect("clicked", generic_clicked, self)

        self.populate(submission)

    def __on_hover(self, *_):
        self.download_btt.set_visible(True)

    def __on_hover_lost(self, *_):
        self.download_btt.set_visible(False)

    def populate(self, submission: Submission):
        submitter = submission["_aSubmitter"]

        def on_finish(cover, sub_pfp):
            idle(self.mod_preview.set_filename, cover)
            idle(self.mod_submitter.set_from_file, sub_pfp)
            idle(self.mod_submitter.set_tooltip_text, submitter["_sName"])

            idle(
                self.mod_feature_type.set_label,
                f"Best of {get_formatted_period(submission['_sPeriod'])}",
            )
            idle(self.mod_name.set_label, submission["_sName"])

            if (n := submission.get("_sDescription", "")) != "":
                idle(self.mod_caption.set_label, n)
            else:
                idle(self.mod_caption.set_visible, False)

        cache_download(submission["_sImageUrl"], submitter["_sAvatarUrl"], cb=on_finish)


@Blueprint("submission-button")
class SubmissionButton(Gtk.Button):
    __gtype_name__ = "SubmissionButton"

    mod_cover: Gtk.Picture = Gtk.Template.Child()
    mod_name: Gtk.Label = Gtk.Template.Child()
    mod_caption: Gtk.Label = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()

    def __init__(self, submission: SubmissionInfo):
        super().__init__(css_classes=["flat"])
        self.submission_id = submission["_idRow"]
        self.type = submission["_sModelName"]

        preview = submission["_aPreviewMedia"]
        if preview.get("_aImages") is not None:
            if len((n := submission["_aPreviewMedia"]["_aImages"])) != 0:
                cache_download(
                    n[0]["_sBaseUrl"] + "/" + n[0]["_sFile"], cb=self.__on_down_finish
                )

        self.mod_name.set_label(submission["_sName"])

        self.connect("clicked", generic_clicked, self)

    def __on_down_finish(self, cover):
        idle(self.stack.set_visible_child_name, "main")
        idle(self.mod_cover.set_filename, cover)
