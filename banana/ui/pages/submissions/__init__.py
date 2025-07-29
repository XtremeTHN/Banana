from gi.repository import Adw, Gtk, Pango

from banana.modules.gamebanana.types import SubmissionInfo
from banana.modules.gamebanana import Gamebanana
from banana.modules.cache import cache_download
from banana.ui.screenshot import Screenshot
from banana.modules.utils import idle
from bs4 import BeautifulSoup
import logging
import re


class Table(Gtk.TextTagTable):
    def __init__(self):
        super().__init__()
        accent = Adw.accent_color_to_rgba(
            Adw.StyleManager.get_default().get_accent_color()
        )

        self.tags = {
            "b": Gtk.TextTag(name="b", weight=700),
            "strong": Gtk.TextTag(name="strong", weight=700),
            "u": Gtk.TextTag(
                name="u",
                underline=Pango.Underline.SINGLE,
            ),
            "a": Gtk.TextTag(
                name="a",
                weight=500,
                foreground_rgba=accent,
                underline=Pango.Underline.SINGLE,
                underline_rgba=accent,
            ),
            "i": Gtk.TextTag(name="i", style=Pango.Style.ITALIC),
            "em": Gtk.TextTag(name="em", style=Pango.Style.ITALIC),
            "li": Gtk.TextTag(name="li", indent=4),
            "h1": Gtk.TextTag(
                name="h1",
                scale=1.6,
                weight=800,
            ),
            "h2": Gtk.TextTag(name="h2", scale=1.4, weight=800),
            "h3": Gtk.TextTag(name="h3", scale=1.2, weight=800),
            "h4": Gtk.TextTag(name="h4", scale=1, weight=800),
            "span": Gtk.TextTag(
                name="span",
            ),
        }

        for _, x in self.tags.items():
            self.add(x)


class SubmissionPage:
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
        self.logger = logging.getLogger(f"{self.__class__.__name__}({submission_id})")
        self.submission_id = submission_id

        spinner = Adw.SpinnerPaintable.new()
        self.loading_status.set_paintable(spinner)
        spinner.set_widget(self.loading_status)

    def remove_html_tags(self, html: str) -> str:
        # Replace <br> and <p> with newlines
        html = re.sub(r"<br\s*/?>", "\n", html)
        html = re.sub(r"</p>", "", html)
        html = re.sub(r"<p>", "", html)

        # Remove all other tags (or handle as needed)
        html = re.sub(r"<.*?>", "", html)

        return html.replace("&nbsp;", "").replace("&", "&amp;")

    def get_formatted_html(self, html: str):
        html = html.replace("&nbsp;", "")
        table = Table()
        buff = Gtk.TextBuffer.new(table)
        soup = BeautifulSoup(html, "html.parser")

        for elem in soup:
            mark = buff.get_insert()
            text = elem.text

            if elem.name == "br":
                buff.insert_at_cursor("\n")
                continue

            if elem.name == "h1":
                text = text + "\n"

            if elem.name == "ul":
                for x in elem.children:
                    buff.insert_with_tags_by_name(
                        buff.get_iter_at_mark(mark), f"- {x.text}\n", "li"
                    )
                continue

            if elem.name is None:
                buff.insert_at_cursor(text)
                continue

            if elem.name not in table.tags:
                self.logger.warning(f"tag not supported: {elem.name}")
                buff.insert_at_cursor(text)
                continue

            buff.insert_with_tags_by_name(buff.get_iter_at_mark(mark), text, elem.name)

        return buff

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
            self.populate_credits(submission["_aCredits"])

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
        self.submission_description.set_buffer(
            self.get_formatted_html(submission["_sText"])
        )
        if (n := submission["_aPreviewMedia"].get("_aImages")) is not None:
            cache_download(*[f"{x['_sBaseUrl']}/{x['_sFile']}" for x in n], cb=finish)
            return
        self.logger.info("No preview media for this submission")

    def populate_credits(self, array_credits):
        if len(array_credits) == 0:
            idle(self.submission_credits_box.append, Adw.ActionRow(title="No credits"))
            return

        for _type in array_credits:
            authors = _type["_aAuthors"]
            if len(authors) == 0:
                row = Adw.ActionRow(title=_type["_sGroupName"], use_markup=False)
            else:
                row = Adw.ExpanderRow(title=_type["_sGroupName"], use_markup=False)

            for author in _type["_aAuthors"]:
                row.add_row(
                    Adw.ActionRow(
                        use_markup=False,
                        css_classes=["property"],
                        title=author.get("_sRole", "Unkown role"),
                        subtitle=author.get("_sName", "Unkown author"),
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
                subtitle = self.remove_html_tags(update["_sText"])

                if (n := update.get("_aChangeLog")) is not None:
                    row = Adw.ExpanderRow(
                        use_markup=False,
                        title=update["_sName"],
                        subtitle=subtitle,
                    )
                    for change in n:
                        subtitle = self.remove_html_tags(change["text"])
                        row.add_row(
                            Adw.ActionRow(
                                use_markup=False,
                                css_classes=["property"],
                                title=change["cat"],
                                subtitle=subtitle,
                            )
                        )
                else:
                    row = Adw.ActionRow(
                        use_markup=False,
                        title=update["_sName"],
                        subtitle=subtitle,
                    )
                idle(self.submission_updates_box.append, row)

    def request_info(self):
        """Calls Gamebanana.get_submission_info"""
        Gamebanana.get_submission_info(
            self.submission_type, self.submission_id, self.populate
        )
