from gi.repository import Adw, Gtk

from banana.modules.gamebanana.types import SubmissionInfo
from banana.modules.utils import idle, remove_html_tags
from banana.modules.gamebanana import Gamebanana
from banana.modules.cache import cache_download
from banana.ui.screenshot import Screenshot
from .html import HtmlView

import logging


class SubmissionPage:
    submission_credits_box: Gtk.ListBox
    submission_updates_box: Gtk.ListBox

    submission_icon: Gtk.Picture
    submission_title: Gtk.Label
    submission_caption: Gtk.Label
    submission_description: HtmlView

    stack: Gtk.Stack
    screenshots_carousel: Adw.Carousel

    likes: Gtk.Label
    views: Gtk.Label
    downloads: Gtk.Label

    loading_status: Adw.StatusPage
    trashed_status: Adw.StatusPage

    info: SubmissionInfo
    submission_type: str
    submission_id: int

    def __init__(self, submission_id: int):
        """
        SubmissionPage handles the display and formatting
        of submission details, credits, and updates within the UI.

        You need to set various class attributes if you wanna use populate functions:
            submission_type:        str
            submission_type: str
            submission_credits_box: Gtk.ListBox
            submission_updates_box: Gtk.ListBox

            submission_icon: Gtk.Picture
            submission_title: Gtk.Label
            submission_caption: Gtk.Label
            submission_description: Gtk.TextView

            stack: Gtk.Stack
            screenshots_carousel: Adw.Carousel

            likes: Gtk.Label
            views: Gtk.Label
            downloads: Gtk.Label

            loading_status: Adw.StatusPage
            trashed_status: Adw.StatusPage
        """
        self.logger = logging.getLogger(
            f"{self.__class__.__name__}(submission_id={submission_id})"
        )
        self.submission_description.set_submission_id(submission_id)
        self.submission_id = submission_id

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

    def populate_extra_widgets(self, submission: SubmissionInfo):
        """override this function pls"""
        return

    def populate(self, submission: SubmissionInfo):
        def finish(cover, *images):
            idle(self.submission_icon.set_filename, cover)

            for img in images:
                s = Screenshot()
                idle(s.pic.set_filename, img)
                idle(self.screenshots_carousel.append, s)

            idle(self.submission_title.set_label, submission["_sName"])
            idle(self.submission_caption.set_label, submission["_aSubmitter"]["_sName"])

            idle(self.likes.set_label, f"{submission['_nLikeCount']:,}")
            idle(self.views.set_label, f"{submission['_nViewCount']:,}")

            if self.submission_type == "Mod":
                idle(self.downloads.set_label, f"{submission['_nDownloadCount']:,}")

            self.populate_updates(self.submission_id)
            self.populate_credits(submission.get("_aCredits"))

            self.populate_extra_widgets(submission)

            idle(self.stack.set_visible_child_name, "main")

        self.set_title(f"{submission['_sName']} - {self.submission_type}")

        if submission["_bIsTrashed"]:
            idle(self.stack.set_visible_child_name, "trashed")
            idle(
                self.trashed_status.set_description,
                f"This submission was trashed: {submission['_aTrashInfo']['_sReason']}",
            )
            return

        self.info = submission

        self.submission_description.html = submission["_sText"]
        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
            return
        self.logger.info("No preview media for this submission")

    def populate_credits(self, array_credits):
        if array_credits is None:
            self.logger.warning("Credits array is none")
            return

        if len(array_credits) == 0:
            idle(self.submission_credits_box.append, Adw.ActionRow(title="No credits"))
            return

        for _type in array_credits:
            authors = _type["_aAuthors"]

            group_name = remove_html_tags(_type["_sGroupName"])
            if len(authors) == 0:
                row = Adw.ActionRow(title=group_name)
            else:
                row = Adw.ExpanderRow(title=group_name)

            for author in _type["_aAuthors"]:
                row.add_row(
                    Adw.ActionRow(
                        css_classes=["property"],
                        title=remove_html_tags(author.get("_sRole", "Unkown role")),
                        subtitle=remove_html_tags(
                            author.get("_sName", "Unkown author")
                        ),
                    )
                )
            idle(self.submission_credits_box.append, row)

    def populate_updates(self, submission_id: str):
        updates = Gamebanana.get_submission_updates(self.submission_type, submission_id)

        for records in updates:
            if len(records) == 0:
                idle(
                    self.submission_updates_box.append,
                    Adw.ActionRow(title="No updates"),
                )
                return

            for update in records:
                title = remove_html_tags(update["_sName"])
                subtitle = remove_html_tags(update["_sText"])
                if (n := update.get("_aChangeLog")) is not None:
                    row = Adw.ExpanderRow(
                        title=title,
                        subtitle=subtitle,
                    )
                    for change in n:
                        row.add_row(
                            Adw.ActionRow(
                                css_classes=["property"],
                                title=remove_html_tags(change["cat"]),
                                subtitle=remove_html_tags(change["text"]),
                            )
                        )
                else:
                    row = Adw.ActionRow(
                        title=title,
                        subtitle=subtitle,
                    )
                idle(self.submission_updates_box.append, row)

    def request_info(self):
        """Calls Gamebanana.get_submission_info"""
        Gamebanana.get_submission_info(
            self.submission_type, self.submission_id, self.populate
        )
